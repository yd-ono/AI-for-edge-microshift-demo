# AI at the Edge with MicroShift

This repository contains the code developed for the talk "[Image recognition on the Edge with Red Hat Device Edge (MicroShift) & Nvidia](https://docs.google.com/presentation/d/1TlnF5NKe7rwOLOIEkOpbbwJpmtJdjL5uYJUUUCsdH0k)" developed by Max Murakami and Robert Bohne based on the fantastic work of [Miguel Angel Ajo and Ricardo Noriega](https://github.com/redhat-et/AI-for-edge-microshift-demo)

The end goal of this demo is to run a face detection and face recognition AI model in a cloud-native fashion using MicroShift in an edge computing scenario. In order to do this, we used the [NVIDIA Jetson](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/) family boards (tested on Jetson Xavier NX).

This demo repository is structured into three different folders:

* model-training: software used to train the model for development purpose, in the demo we train our model via ... TODO
* webapp: Flask server that receives video streams from the cameras and performs face detection and recognition.

## Running MicroShift (jetson L4T)

We assume that you have installed the standard L4T operating system specific to your Jetson board, and it is ready to install some packages (as root).

```
apt install -y curl jq runc iptables conntrack nvidia-container-runtime nvidia-container-toolkit
```

Disable firewalld:

```
systemctl disable --now firewalld
```

Install CRI-O 1.21 as our container runtime:

```
curl https://raw.githubusercontent.com/cri-o/cri-o/v1.21.7/scripts/get | bash

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
export VERSION=4.8.0-0.microshift-2022-02-02-194009

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
curl -LO https://mirror.openshift.com/pub/openshift-v4/arm64/clients/ocp/stable-4.9/openshift-client-linux.tar.gz
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

## AI Web App

The final step is to deploy the AI Web App that will perform face detection and face recognition. This pod is basically a Flask server that will get the streams of the cameras once they are connected, and start working on a discrete number of frames.

Let's deploy the AI models on MicroShift:

```
oc new-project ai-for-edge
oc apply -f webapp.deploy.yaml
```

After few seconds:

```
oc get pods

NAME                         READY   STATUS    RESTARTS   AGE
webapp-67dd6b46fc-bqgbs   1/1     Running   2          2m33s
```

Check the hostname of the route:

```
$ oc get routes
NAME     HOST/PORT                          PATH   SERVICES   PORT       TERMINATION   WILDCARD
webapp   webapp-ai-for-edge.cluster.local          webapp     5000-tcp                 None
```

MicroShift has mDNS built-in capabilities, and this route will be automatically announced, so the cameras can register to this service, and start streaming video.

Looking at the camserver logs, we can see this registration process:

```
oc logs -f deployment/webapp -c webapp

[2022-12-30 12:24:32,647] INFO in faces: Load model from disk: /model/model.data
[2022-12-30 12:24:32,649] INFO in faces: Known faces loaded from disk.
 * Serving Flask app 'server'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://10.85.0.9:5000
Press CTRL+C to quit
10.85.0.1 - - [30/Dec/2022 12:24:33] "GET /favicon.ico HTTP/1.1" 404 -
```

Finally, open a browser with the following URL:

```
http://webapp-ai-for-edge.cluster.local
```

This web will show you the feeds of the camera and you will be able to see how faces are detected.

![Screenshot](screenshot.png)

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