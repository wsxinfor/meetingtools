# FunASR部署说明：开发机 vs 服务器

## 1. 结论

开发阶段：FunASR可以安装在开发机器上，用于调试和验证。

生产阶段：FunASR应该部署在服务器或独立容器中，由FastAPI统一调用。

## 2. 开发机安装的用途

- 验证模型效果
- 调试音频预处理
- 调试VAD切分
- 调试ASR调用代码

这不是最终运行架构。

## 3. 正式部署架构

```text
PC/手机浏览器
↓
Vue前端
↓
FastAPI后端
↓
ASR服务（FunASR/SenseVoice）
↓
返回转写结果
```

## 4. 推荐服务拆分

```text
backend: FastAPI业务服务       → 宿主机端口 6011
asr:     FunASR识别服务        → 宿主机端口 6013
llm:     Ollama/vLLM服务      → 宿主机端口 6014
postgres: 数据库               → 宿主机端口 6012
minio:   文件存储，可选         → 宿主机端口 6015
```

## 5. 代码设计要求

业务代码不要直接依赖具体模型，应通过AsrProvider抽象：

```python
class AsrProvider:
    def transcribe_file(self, audio_path: str):
        raise NotImplementedError
```

这样可以支持：

- 开发机本地FunASR
- 服务器FunASR
- HTTP ASR服务
- Whisper备用引擎
