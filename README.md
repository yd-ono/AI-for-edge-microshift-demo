# AI at the Edge with MicroShift

This repository contains the code developed for the talk "[Image recognition on the Edge with Red Hat Device Edge (MicroShift) & Nvidia](https://docs.google.com/presentation/d/1TlnF5NKe7rwOLOIEkOpbbwJpmtJdjL5uYJUUUCsdH0k)" developed by Max Murakami and Robert Bohne based on the fantastic work of [Miguel Angel Ajo and Ricardo Noriega](https://github.com/redhat-et/AI-for-edge-microshift-demo)

The end goal of this demo is to run a face detection and face recognition AI model in a cloud-native fashion using MicroShift in an edge computing scenario. In order to do this, we used the [NVIDIA Jetson](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/) family boards (tested on Jetson Xavier NX).

This demo repository is structured into three different folders:

* model-training: software used to train the model for development purpose, in the demo we train our model via ... TODO
* webapp: Flask server that receives video streams from the cameras and performs face detection and recognition.

## Running MicroShift (jetson L4T)

At this point, we have programmed our ESP32 cameras. We assume that you have installed the standard L4T operating system specific to your Jetson board, and it is ready to install some packages (as root).

```
apt install -y curl jq runc iptables conntrack nvidia-container-runtime nvidia-container-toolkit
```

Disable firewalld:

```
systemctl disable --now firewalld
```

Install CRI-O as our container runtime:

```
curl https://raw.githubusercontent.com/cri-o/cri-o/main/scripts/get | bash

```

Configure CRI-O in order to use the NVIDIA Container Runtime


```
rm /etc/crio/crio.conf.d/*

cat << EOF > /etc/crio/crio.conf.d/10-nvidia-runtime.conf
[crio.runtime]
default_runtime = "nvidia"

[crio.runtime.runtimes.nvidia]
runtime_path = "/usr/bin/nvidia-container-runtime"
EOF

cat << EOF > /etc/crio/crio.conf.d/01-crio-runc.conf
[crio.runtime.runtimes.runc]
runtime_path = "/usr/sbin/runc"
runtime_type = "oci"
runtime_root = "/run/runc"
EOF

rm -rf /etc/cni/net.d/10-crio-bridge.conf
```

Download MicroShift binary:

```
export ARCH=arm64
export VERSION=$(curl -L -s https://api.github.com/repos/redhat-et/microshift/releases | grep tag_name | head -n 1 | cut -d '"' -f 4)
curl -LO https://github.com/redhat-et/microshift/releases/download/$VERSION/microshift-linux-${ARCH}
mv microshift-linux-${ARCH} /usr/bin/microshift; chmod 755 /usr/bin/microshift
```
Create the MicroShift's systemd service:

```
cat << EOF > /usr/lib/systemd/system/microshift.service
[Unit]
Description=MicroShift
After=crio.service

[Service]
WorkingDirectory=/usr/bin/
ExecStart=/usr/bin/microshift run
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF
```

Enable and run CRI-O and MicroShift services:
```
systemctl enable crio --now
systemctl enable microshift.service --now
```
Download and install the oc client:

```
curl -LO https://mirror.openshift.com/pub/openshift-v4/arm64/clients/ocp/stable/openshift-client-linux.tar.gz
tar xvf openshift-client-linux.tar.gz
chmod +x oc
mv oc /usr/local/bin
```

Set Kubeconfig environment variable:

```
export KUBECONFIG=/var/lib/microshift/resources/kubeadmin/kubeconfig
```

If MicroShift is up and running, after a couple of minutes you should see the following pods:

```
root@jetson-nx:~# oc get pod -A
NAMESPACE                       NAME                                  READY   STATUS    RESTARTS   AGE
kube-system                     kube-flannel-ds-7rz4d                 1/1     Running   0          17h
kubevirt-hostpath-provisioner   kubevirt-hostpath-provisioner-9m9mc   1/1     Running   0          17h
openshift-dns                   dns-default-6pbkt                     2/2     Running   0          17h
openshift-dns                   node-resolver-g4d8g                   1/1     Running   0          17h
openshift-ingress               router-default-85bcfdd948-tsk29       1/1     Running   0          17h
openshift-service-ca            service-ca-7764c85869-dvdtm           1/1     Running   0          17h

```

Now, we have our cloud-native platform ready to run workloads. Think about this: we have an edge computing optimized Kubernetes distribution ready to run an AI workload, and make use of the integrated GPU from the NVIDIA Jetson board. It's awesome!

## AI models

The final step is to deploy the AI models that will perform face detection and face recognition. This pod is basically a Flask server that will get the streams of the cameras once they are connected, and start working on a discrete number of frames.

Let's deploy the AI models on MicroShift:

```
oc apply -f server/cam-server.yaml
```

After few seconds:

```
oc get pods

NAME                         READY   STATUS    RESTARTS   AGE
cameras-ap-b6b6c9c96-krm45   1/1     Running   0          4m37s
camserver-cc996fd86-pkm45    1/1     Running   0          42s
```

We also need to create a service and expose a route for this pod:

```
oc expose deployment camserver
oc expose service camserver --hostname microshift-cam-reg.local
```

MicroShift has mDNS built-in capabilities, and this route will be automatically announced, so the cameras can register to this service, and start streaming video.

Looking at the camserver logs, we can see this registration process:

```
oc logs camserver-cc996fd86-pkm45

 * Serving Flask app 'server' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on all addresses.
   WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://10.85.0.36:5000/ (Press CTRL+C to quit)
[2022-01-21 11:18:46,203] INFO in server: camera @192.168.66.89 registered with token a53ca190
[2022-01-21 11:18:46,208] INFO in server: starting streamer thread
[2022-01-21 11:19:34,674] INFO in server: starting streamer thread
10.85.0.1 - - [21/Jan/2022 11:19:34] "GET /register?ip=192.168.66.89&token=a53ca190 HTTP/1.1" 200 -
```

Finally, open a browser with the following URL:

```
http://microshift-cam-reg.local/video_feed
```

This web will show you the feeds of all the cameras that have been registered and you will be able to see how faces are detected.


## Conclusion

This demo is just a simple use case of what an edge computing scenario would look like. Running AI/ML models on top of an embedded system like the NVIDIA Jetson family, and leveraging cloud-native capabilities with MicroShift.

We hope you enjoy it!

# Installing manifests

MicroShift has a feature to auto-apply manifests from disk during startup,
you can find the documentation here https://microshift.io/docs/user-documentation/manifests/

After applying the new manifests restart MicroShift with `systemctl restart microshift`.

```bash

mkdir -p /var/lib/microshift/manifests
cd /var/lib/microshift/manifests
```

TODO Add webapp deployment manifests...