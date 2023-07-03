# AI at the Edge with MicroShift

このリポジトリには、[Miguel Angel Ajo and Ricardo Noriega](https://github.com/redhat-et/AI-for-edge-microshift-demo)の素晴らしい仕事に基づいてMax MurakamiとRobert Bohneが開発した講演「[Red Hat Device Edge (MicroShift) & Nvidiaによるエッジでの画像認識](https://docs.google.com/presentation/d/1TlnF5NKe7rwOLOIEkOpbbwJpmtJdjL5uYJUUUCsdH0k)」のために開発されたコードが含まれています。

このデモの最終目標は、エッジ・コンピューティング・シナリオでMicroShiftを使用して、クラウドネイティブな方法で顔検出と顔認識AIモデルを実行することです。そのために、[NVIDIA Jetson](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/)ファミリーのボード（Jetson Xavier NXでテスト）を使用しました。


![Overview](overview.png)

このデモリポジトリは、さまざまなフォルダ/コンテンツで構成されています：

|コンポーネント/フォルダ|概要|デモでの必要性|
|---|---|---|
|`openshift-local/`|[OpenShift Single NodeまたはOpenShift Local環境をブートストラップするためのすべての情報。基本的なOpenShift GitOpsとOpenShift Pipelinesのデプロイと設定。](crc-bootstrap/README.md)| Yes |
|`model-training-pipeline` |  顔画像に基づく顔認識モデルの学習に必要なステップを含むJupyterノートブック。 | Yes |
|`local-registry-deploy/`|NVIDIA Jetsonで展開されるエッジのレジストリ| Yes |
|`webapp/`| カメラからのビデオストリームを受信し、顔検出と認識を実行するFlaskサーバ。https://quay.io/rbohne/ai-for-edge-microshift-demo:webapp | Yes |
|`webapp-deploy/` | Deployment of webapp via GitOps model. | Yes |
|`container-images/cpu-only/`|Pythonウェブアプリケーション用のCPUのみのベースイメージ。https://quay.io/rbohne/ai-for-edge-microshift-demo:cpu-only | No |
|`container-images/l4t-cuda-dlib/`|CUDA/GPU 対応の Python Web アプリケーション用ベースイメージ。https://quay.io/rbohne/ai-for-edge-microshift-demo:l4t-cuda-dlib から入手可能。 | No |
|`container-images/model-container/`|モデルのコンテナとデータストアを初期化する。デモ中にビルドする。サンプルはこちら: https://quay.io/rbohne/ai-for-edge-microshift-demo:model |No |
|`model-training/`|ラップトップやJetsonで、ローカルモデルのトレーニングができる。 | No |
|`tinyproxy-for-jetson/` | [NVIDIA Jetson用のプロキシサーバーを起動するプロキシイメージ]( tinyproxy-for-jetson/README.md ) | No |

## デモの実行

### 1) Webappへのアクセス:

http://webapp-ai-for-edge.cluster.local/

=> Nothing recognitced

### 2) モデルの(再)学習

1. RHODSダッシュボードで、データサイエンスプロジェクトの`model training`ワークベンチを開きます。
2. face-images`フォルダを開きます。トレーニングワークフローは、このフォルダ内の末尾が`.jpg`である各顔画像の埋め込みを作成します。ファイル名（末尾を除く）を対応する人物の名前として使用します。このフォルダに新しい顔画像をアップロードすることで、新しい顔認識モデルを学習し、それによってエッジアプリケーションが新しい顔を認識できるようになります。
3. クローンしたリポジトリの `model-training-pipeline` フォルダ内の `training-workflow.ipynb` ノートブックを開きます。
4. 左のツールバーにある `Object Storage Browser` JupyterLab 拡張を開く。S3のエンドポイントと認証情報を入力し、ログインします。models`バケットを含むS3バケットのリストが表示されます。models`バケットを開く。
5. ノートブックのセルを上から下に順番に実行します。
6. セルを実行すると、オブジェクトストレージブラウザに新しいフォルダが表示されるはずです。その名前は、アップロードされたモデルのタイムスタンプ（バージョン）を示しています。そのフォルダの中に、パッケージ化されたモデルのバイナリである `model.data` というファイルがあるはずです。

これでMLの開発とトレーニングの段階は終了です。次のステップでは、学習済みのモデルをコンテナにパッケージして、ターゲットのエッジプラットフォームに出荷できるようにします。


### 3) MLモデルをコンテナに入れ、パイプラインでエッジデバイスへPush：

https://console-openshift-console.apps-crc.testing/pipelines/ns/rhte-pipeline

### 4) `webapp-deploy/deployment.yaml`をアップデート

Example diff:
```diff
$ git diff webapp-deploy/deployment.yaml
diff --git a/webapp-deploy/deployment.yaml b/webapp-deploy/deployment.yaml
index 10da805..1824e47 100644
--- a/webapp-deploy/deployment.yaml
+++ b/webapp-deploy/deployment.yaml
@@ -33,7 +33,7 @@ spec:
     spec:
       serviceAccountName: privileged
       initContainers:
-      - image: default-registry.cluster.local/ai-for-edge/model:2302011505
+      - image: default-registry.cluster.local/ai-for-edge/model:2302011506
         imagePullPolicy: IfNotPresent
         name: model
         volumeMounts:
$
```

### 5) OpenShift GitOpsでロールアウト
    https://openshift-gitops-server-openshift-gitops.apps-crc.testing/applications/openshift-gitops/ai-for-edge-webapp?view=tree&resource=

### 6) WebAppを再び表示し、今度は緑のボックスで表示

### 7) オプション： tegrastats経由でGPUの統計情報を表示する

### Video of the Demo:

[![AI for edge deom video](https://img.youtube.com/vi/8dHpNAPSgZ0/0.jpg)](https://www.youtube.com/watch?v=8dHpNAPSgZ0 "AI for edge deom video")

## Hardware Set Up

![hardware-set-up](hardware-set-up.png)


## セットアップ

デモは、エンドツーエンドのMLワークフローの環境を表す2つのOpenShiftインスタンス上にセットアップされています：
- モデルのトレーニングとコンテナの構築のためのOpenShiftクラスタ（パブリッククラウドの中央データセンターにあるデータサイエンス環境）
- エッジロケーションのデバイスにデプロイされたMicroShiftインスタンス。AIウェブアプリをホストし、入力されたビデオストリームを処理し、カプセル化された顔認識モデルに基づいて顔認識を実行する。


### 中央のOCPクラスタにモデルのトレーニングとパッケージングをセットアップする

S3ストレージインスタンスをセットアップしているか、既存のS3ストレージインスタンスに書き込み権限を持っていると仮定する。

1. Operator Hubから`Red Hat OpenShift Data Science` operatorをインストール
2. Operator Hubから`Red Hat OpenShift Pipelines` operator (1.7 or 1.8) をインストール
3. [manifests/face-recognition-notebook.yaml](manifests/face-recognition-notebook.yaml)を`redhat-ods-applications` namespaceへデプロイ
4. RHODSのダッシュボードを開く (ツールバー上に追加された`Red Hat OpenShift Data Science` メニューで開けます).
5. `Data Science Projects`タブにて, `Create data science project`を選択します.そして、 名前へ`demo-project`を入力し、`Create`を押下します。
6. `Create workbench`を選択し、以下を入力
    - Name: `model training`
    - Notebook image: `Face recognition Elyra`
    - Select `Create workbench`
7. S3ストレージ内で, `models`と言う名前のバケットを作成します。
8. RHODS ダッシュボードにて, `Add data connection`を選択し、以下を入力します。
    - Name: `models`
    - AWS_ACCESS_KEY: your S3 access key
    - AWS_SECRET_ACCESS_KEY: your S3 secret key
    - AWS_S3_ENDPOINT: your S3 endpoint URL
    - AWS_S3_BUCKET: `models`
    - Connected workbench: `model training`
    - Select `Add data connection`
9. `model training` workbenchの状態を確認します。状態が`Running`となったら、`Open`を選択してください。
10. workbenchを開き、左側のツールバーから、`Git client`を選択します。そして、`Clone a Repository`を選択し、GitリポジトリのURLを指定して、`Clone`を選択してください。

### Setting up OpenShift Local / OpenShift Single Node

ラップトップへOpenShift.localをインストールします。OpenShift.localのインストール方法は以下を参照してください。
 * [officia documetation](https://developers.redhat.com/products/openshift-local/overview)


OpenShift.localをインストールしたら、以下のマニフェストをapplyして、OpenShift PipelinesとOpenShift GitOpsをインストールします。
```bash
oc apply -k openshift-local/
```

次に、OpenShift GitOps(ArgoCD)へエッジデバイスのKubernetesクラスタを追加します。

```bash
# MicroShiftのKubeconfigをローカルへコピー
scp redhat@microshift.local:/var/lib/microshift/resources/kubeadmin/microshift.local ./
vi microshift.local
...
    server: https://$MICROSHIFT_IP_ADDRESS:6443
  name: microshift
...
export KUBECONFIG=/path/to/microshift.local

# OpenShift.localのOpenShift GitOpsへログイン
PASSWORD=$(oc get secret -n openshift-gitops openshift-gitops-cluster -o jsonpath='{.data.admin\.password}' | base64 -d)
argocd login --username admin --password $PASSWORD openshift-gitops-server-openshift-gitops.apps-crc.testing --insecure

# ArgoCDインスタンスへクラスタを追加
argocd cluster add $(oc config current-context)
```

`argocd cluster list`の実行結果例:
```bash
argocd cluster list
SERVER                          NAME        VERSION  STATUS      MESSAGE                                                  PROJECT
https://$MICROSHIFT_IP:6443       microshift  1.26     Successful                                                           
https://kubernetes.default.svc  in-cluster           Unknown     Cluster has no applications and is not being monitored. 
```

```bash
unset KUBECONFIG
```

ArgoCD Applicationをapplyします。
```bash
cat openshift-local/ai-for-edge-webapp.application.yaml | envsubst | oc apply -f -
cat openshift-local/registry.application.yaml | envsubst | oc apply -f -
```

MicroShiftの`/etc/hosts`へローカルレジストリのURLを追記します。
```bash
echo "$MICROSHIFT_IP default-registry.cluster.local" >> /etc/hosts
```

そして、`/etc/crio.conf`へ作成したローカルレジストリを`insecure registry`として追記します。
```bash
sudo su
cat /etc/crio/crio.conf
...
insecure_registries=["default-registry.cluster.local"]
...

systemctl restart crio
```

`push-model-to-edge-pipeline` Pipelineを作成します。
```bash
# Create project/namespace
oc new-project rhte-pipeline
cat push-model-to-edge-pipeline/buildah-with-dns.task.yaml | envsubst | oc apply -f -
# You may want to adjust the defaults of S3_ENDPOINT_URL, BUCKET_NAME,
#      git_repository_url.. first
oc apply -f push-model-to-edge-pipeline/push-model-to-edge.pipeline.yaml

# Add S3 bucket access

export AWS_ACCESS_KEY=...
export AWS_SECRET_ACCESS_KEY=...

cat >credentials <<EOF
[default]
aws_access_key_id     = ${AWS_ACCESS_KEY}
aws_secret_access_key = ${AWS_SECRET_ACCESS_KEY}
EOF

oc create secret generic aws-credentials --from-file=credentials=credentials
```


###　ローカルプロキシをエッジデバイス上で実行する

**Build**
```bash
cd tinyproxy-for-jetson/
podman build -t proxy:latest .
```

**Run**
```bash
podman run -ti --rm \
    -p 192.168.5.1:8080:8080 \
    --name proxy proxy:latest
```

### Running MicroShift (jetson L4T)

以下の手順をrootユーザで実行します。

```
apt install -y curl jq runc iptables conntrack nvidia-container-runtime nvidia-container-toolkit
```

firewalldを無効化:

```
systemctl disable --now firewalld
```

CRI-O 1.21をインストール:

```
curl https://raw.githubusercontent.com/cri-o/cri-o/v1.21.7/scripts/get | bash

```

NVIDIA Container Runtimeを設定：


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

MicroShiftバイナリをインストール：

```
export ARCH=arm64
export VERSION=4.8.0-0.microshift-2022-02-02-194009

curl -LO https://github.com/redhat-et/microshift/releases/download/$VERSION/microshift-linux-${ARCH}
mv microshift-linux-${ARCH} /usr/bin/microshift; chmod 755 /usr/bin/microshift
```
MicroShiftのsystemd Serviceを作成：

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

CRI-OとMicroShiftを起動：

```
systemctl enable crio --now
systemctl enable microshift.service --now
```

CLIコマンド(`oc`)をインストール：

```
curl -LO https://mirror.openshift.com/pub/openshift-v4/arm64/clients/ocp/stable-4.9/openshift-client-linux.tar.gz
tar xvf openshift-client-linux.tar.gz
chmod +x oc
mv oc /usr/local/bin
```

Kubeconfigを設定：

```
export KUBECONFIG=/var/lib/microshift/resources/kubeadmin/kubeconfig
```

MicroShiftが正常起動したら、以下の結果となります。

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

### AI Web App

最後のステップは、顔検出と顔認識を行うAIウェブアプリをデプロイするステップです。
デプロイされるPodは基本的にFlaskサーバーで、カメラが接続されるとストリームを取得し、個別のフレーム数で処理を開始します。

MicroShift上にAIをデプロイしましょう。

```
oc new-project ai-for-edge
oc apply -f webapp.deploy.yaml
```

数秒待つと・・・

```
oc get pods

NAME                         READY   STATUS    RESTARTS   AGE
webapp-67dd6b46fc-bqgbs   1/1     Running   2          2m33s
```

Routeを確認します。

```
$ oc get routes
NAME     HOST/PORT                          PATH   SERVICES   PORT       TERMINATION   WILDCARD
webapp   webapp-ai-for-edge.cluster.local          webapp     5000-tcp                 None
```

MicroShiftにはmDNS機能が内蔵されており、このルートは自動的にアナウンスされるため、カメラはこのサービスに登録し、ビデオのストリーミングを開始することができます。
カムサーバーのログを見ると、このような登録プロセスが見られます。


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

ブラウザを開き、以下のURLへアクセスします：

```
http://webapp-ai-for-edge.cluster.local
```

このウェブでは、カメラのフィードが表示され、顔がどのように検出されるかを見ることができる。

![Screenshot](screenshot.png)

## Configuration options

|環境変数|概要|デフォルト|RHTE 2023設定|Lunch&Learn Munich
|---|---|---|---|---|
|`MODEL_FILENAME`|Model to load during startup.|`model.data`|via init container|Default|
|`VIDEO_DEVICE_ID`|Video device to open:<br/>`cv2.VideoCapture(int(os.environ.get('VIDEO_DEVICE_ID', 0)),cv2.CAP_V4L2)`|`0`|`0`|`0`|
|`CAP_PROP_FRAME_WIDTH`|`cap.set(cv2.CAP_PROP_FRAME_WIDTH()`|`1280`|`800`|`800`|
|`CAP_PROP_FRAME_HEIGHT`|`cap.set(cv2.CAP_PROP_FRAME_HEIGHT()`|`720`|`600`|`600`|
|`FACE_RATIO`|Scale down the image to XX<br/>`small_frame = cv2.resize(frame, (0, 0), fx=FACE_RATIO, fy=FACE_RATIO)`|`0.25`|`1`|`1`
|`FACE_LOC_MODEL`|model – Which face detection model to use: <br/><li>`hog` is less accurate but faster on CPUs.</li><li>`cnn` is a more accurate deep-learning model which is GPU/CUDA accelerated (if available).</li>Python function [face_locations](https://face-recognition.readthedocs.io/en/latest/face_recognition.html#face_recognition.api.face_landmarks)|`hog`|`cnn`|`cnn`|
|`FACE_LOC_NTU`|**N**umber_f_**T**imes_to_**U**psample – How many times to upsample the image looking for faces. Higher numbers find smaller faces.<br/>Python function [face_locations](https://face-recognition.readthedocs.io/en/latest/face_recognition.html#face_recognition.api.face_landmarks)|`1`|`2`|`2`|
|`VIDEO_PROCESSING_FPS`|Set amount of FPS they have to capture and process.|`1`|`30`*|`1`|
|`WEB_LOGLEVEL`|Loglevel for the webapp: `CRITICAL`, `ERROR`, `WARNING`,`INFO` or `DEBUG`|`INFO`|`INFO`|`INFO`|
*) Because the setting was not available at RHTE 2023

# JetsonでのWebappの開発
## Base Imageの作成

```bash
cd container-images/cpu-only
./build-and-push.sh 
```

Tekton Pipelineでは、このBase Imageを使用して、Webアプリのコンテナイメージを作成します。

```bash

podman run -ti --rm \
    --runtime /usr/bin/nvidia-container-runtime  \
    --net host \
    --privileged \
    -v $(pwd):/app:z \
    -e VIDEO_DEVICE_ID=0 \
    -e FLASK_APP=server \
    -e LC_ALL=C.UTF-8 \
    -e LANG=C.UTF-8 \
    -e MODEL_TRAINING_YAML=/app/model-training/data/metadata.yaml \
    -e MODEL_FILENAME=/app/model-training/model.data \
    default-registry.cluster.local/ai-for-edge/webapp:latest \
    bash

# First time train the model
root@jetson:/app# cd /app/model-training/
root@jetson:/app/model-training# ./model-training.py
Train face of Robert Bohne => /app/model-training/data/rbohne.jpg
Known faces backed up to disk: /app/model-training/model.data

# Run the Server
root@jetson:/app# cd /app/webapp/
root@jetson:/app/webapp# python3 -m flask run --host 0.0.0.0
[2022-12-30 16:45:04,064] INFO in faces: Load model from disk: model.data
[2022-12-30 16:45:04,065] CRITICAL in faces: No model face found
 * Serving Flask app 'server'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.66.244:5000
Press CTRL+C to quit


```

## 異なるバージョンとGPUサポートをチェック

|コンポーネント|コマンド|
|---|---|
| nvidia-l4t-core | `dpkg-query --showformat='${Version}' --show nvidia-l4t-core` |
| OpenCV | ` python3 -c 'import cv2;print(cv2.getBuildInformation())' |grep cuda ` |
| dlib | `python3 -c 'import dlib; print(dlib.DLIB_USE_CUDA);print(dlib.cuda.get_num_devices())'` |
| CUDA | `/usr/local/cuda/bin/nvcc --version` |

## 参考情報
* <https://docs.opencv.org/4.x/d2/de6/tutorial_py_setup_in_ubuntu.html>
* <https://developer.ridgerun.com/wiki/index.php/How_to_Capture_Frames_from_Camera_with_OpenCV_in_Python>
* <https://forums.developer.nvidia.com/t/issues-with-dlib-library/72600>
* <https://catalog.ngc.nvidia.com/orgs/nvidia/containers/l4t-cuda>
* [How to setup nvidia-container-runtime and podman/runc](https://gist.github.com/bernardomig/315534407585d5912f5616c35c7fe374)
* <https://developer.nvidia.com/embedded/learn/tutorials/first-picture-csi-usb-camera>
* <https://learnopencv.com/opencv-dnn-with-gpu-support/>
* <https://medium.com/@ageitgey/build-a-hardware-based-face-recognition-system-for-150-with-the-nvidia-jetson-nano-and-python-a25cb8c891fd>
* <https://repo.download.nvidia.com/jetson/>
* <https://community.theta360.guide/t/ricoh-theta-v-livestreaming-with-jetson-xavier-ros-opencv-nuc/7105/32>
* <https://github.com/mmaaz60/SkipVideoFramesUsingOpenCV>

## まとめ

このデモは、エッジコンピューティングのシナリオがどのようなものかを示す簡単なユースケースです。Nvidia Jetsonファミリーのような組み込みシステムの上でAI/MLモデルを実行し、MicroShiftでクラウドネイティブ機能を活用します。

どうぞお楽しみください！
