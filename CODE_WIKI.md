# Trae Agent Code Wiki

## 项目介绍

**Trae Agent** 是一个基于 LLM 的软件工程任务智能体。它提供了强大的 CLI 接口，可以理解自然语言指令并使用各种工具执行复杂的软件工程工作流程。

- **技术报告**: [arXiv:2507.23370](https://arxiv.org/abs/2507.23370)
- **Python 版本**: 3.12+
- **许可证**: MIT

### 主要特性

- 🌊 **Lakeview**: 为智能体步骤提供简短精炼的摘要
- 🤖 **多 LLM 支持**: 支持 OpenAI、Anthropic、Doubao、Azure、OpenRouter、Ollama 和 Google Gemini API
- 🛠️ **丰富的工具生态**: 文件编辑、bash 执行、顺序思考等
- 🎯 **交互模式**: 用于迭代开发的对话式界面
- 📊 **轨迹记录**: 详细记录所有智能体动作，便于调试和分析
- ⚙️ **灵活配置**: 支持环境变量的 YAML 配置
- 🐳 **Docker 支持**: 可在 Docker 容器环境中运行

---

## 项目架构

### 目录结构

```
trae-agent/
├── trae_agent/          # 核心源代码
│   ├── agent/           # 智能体实现
│   ├── prompt/          # 系统提示词
│   ├── tools/           # 工具系统
│   ├── utils/           # 工具函数
│   └── __init__.py
├── docs/                # 文档
├── tests/               # 测试
├── evaluation/          # 评估框架
├── pyproject.toml       # 项目配置
└── README.md
```

### 核心模块依赖关系

```
CLI (cli.py)
    ↓
Agent Factory (agent/__init__.py, agent/agent.py)
    ↓
Base Agent (agent/base_agent.py)
    ↓
TraeAgent (agent/trae_agent.py)
    ↓
├── LLM Client (utils/llm_clients/)
├── Tools (tools/)
└── Trajectory Recorder (utils/trajectory_recorder.py)
```

---

## 主要模块详解

### 1. CLI 模块 (`trae_agent/cli.py`)

**职责**: 提供命令行接口，处理用户输入，配置管理，启动智能体执行。

**主要命令**:
- `trae-cli run`: 执行单个任务
- `trae-cli interactive`: 启动交互模式
- `trae-cli show-config`: 显示当前配置
- `trae-cli tools`: 列出可用工具

**关键类/函数**:

| 类/函数 | 描述 |
|---------|------|
| `cli()` | Click 主命令组 |
| `run()` | 执行任务的命令函数 |
| `interactive()` | 交互模式命令 |
| `show_config()` | 配置显示命令 |
| `resolve_config_file()` | 配置文件路径解析（向后兼容） |
| `check_docker()` | Docker 环境检查 |

---

### 2. 智能体模块 (`trae_agent/agent/`)

#### 2.1 智能体工厂 (`agent/agent.py`)

**职责**: 智能体类型管理和创建入口。

**核心类**:

```python
class Agent:
    def __init__(
        self,
        agent_type: AgentType | str,
        config: Config,
        trajectory_file: str | None = None,
        cli_console: CLIConsole | None = None,
        docker_config: dict | None = None,
        docker_keep: bool = True,
    ): ...
    
    async def run(self, task: str, extra_args: dict, tool_names: list): ...
```

**关键方法**:
- `__init__()`: 初始化智能体，设置轨迹记录器，创建具体智能体实例
- `run()`: 执行任务，初始化 MCP 工具，管理执行流程

#### 2.2 TraeAgent (`agent/trae_agent.py`)

**职责**: 专门用于软件工程任务的智能体实现。

**核心类**:

```python
class TraeAgent(BaseAgent):
    def __init__(self, trae_agent_config: TraeAgentConfig, 
                 docker_config: dict = None, docker_keep: bool = True): ...
    
    async def initialise_mcp(self): ...
    async def discover_mcp_tools(self): ...
    def new_task(self, task: str, extra_args: dict, tool_names: list): ...
    async def execute_task(self) -> AgentExecution: ...
    def get_system_prompt(self) -> str: ...
    def get_git_diff(self) -> str: ...
    async def cleanup_mcp_clients(self) -> None: ...
```

**核心功能**:
- 任务初始化和管理
- MCP (Model Context Protocol) 工具发现和初始化
- Git 差异获取
- 任务完成检测
- 轨迹记录管理

#### 2.3 BaseAgent (`agent/base_agent.py`)

**职责**: 所有智能体的基类，提供核心执行循环。

---

### 3. 工具模块 (`trae_agent/tools/`)

#### 3.1 工具基类 (`tools/base.py`)

**职责**: 定义工具接口和工具执行器。

**核心类/数据结构**:

| 类/结构 | 描述 |
|---------|------|
| `Tool` | 所有工具的抽象基类 |
| `ToolParameter` | 工具参数定义 |
| `ToolCall` | 工具调用表示 |
| `ToolResult` | 工具执行结果 |
| `ToolExecutor` | 工具执行管理器 |

**Tool 类抽象方法**:
```python
class Tool(ABC):
    @abstractmethod
    def get_name(self) -> str: ...
    
    @abstractmethod
    def get_description(self) -> str: ...
    
    @abstractmethod
    def get_parameters(self) -> list[ToolParameter]: ...
    
    @abstractmethod
    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult: ...
```

#### 3.2 具体工具实现

| 工具名称 | 类名 | 描述 |
|----------|------|------|
| `bash` | `BashTool` | 执行 bash 命令 |
| `str_replace_based_edit_tool` | `TextEditorTool` | 基于字符串替换的文本编辑 |
| `json_edit_tool` | `JSONEditTool` | JSON 结构编辑 |
| `sequentialthinking` | `SequentialThinkingTool` | 顺序思考工具 |
| `task_done` | `TaskDoneTool` | 任务完成标记 |
| `ckg` | `CKGTool` | CKG 数据库操作工具 |

**工具注册**:
```python
tools_registry: dict[str, type[Tool]] = {
    "bash": BashTool,
    "str_replace_based_edit_tool": TextEditorTool,
    "json_edit_tool": JSONEditTool,
    "sequentialthinking": SequentialThinkingTool,
    "task_done": TaskDoneTool,
    "ckg": CKGTool,
}
```

---

### 4. 配置模块 (`trae_agent/utils/config.py`)

**职责**: 管理项目配置，支持 YAML 配置文件、环境变量和命令行参数。

**核心数据类**:

| 类 | 描述 |
|----|------|
| `ModelProvider` | 模型提供商配置 |
| `ModelConfig` | 模型配置 |
| `MCPServerConfig` | MCP 服务器配置 |
| `AgentConfig` | 智能体配置基类 |
| `TraeAgentConfig` | TraeAgent 配置 |
| `LakeviewConfig` | Lakeview 功能配置 |
| `Config` | 主配置类 |

**配置优先级**:
```
命令行参数 > 配置文件 > 环境变量 > 默认值
```

**Config 类主要方法**:
```python
@classmethod
def create(cls, config_file: str, config_string: str) -> "Config": ...

def resolve_config_values(
    self,
    provider: str = None,
    model: str = None,
    model_base_url: str = None,
    api_key: str = None,
    max_steps: int = None,
) -> "Config": ...
```

---

### 5. LLM 客户端模块 (`trae_agent/utils/llm_clients/`)

**职责**: 为多个 LLM 提供商提供统一的接口。

**支持的提供商**:
- OpenAI
- Anthropic
- Azure
- Ollama
- OpenRouter
- Doubao
- Google Gemini

**核心类**:

| 类 | 描述 |
|----|------|
| `LLMProvider` | 提供商枚举 |
| `LLMClient` | 主客户端包装器 |
| `BaseLLMClient` | 客户端基类 |
| `OpenAIClient` / `AnthropicClient` / ... | 具体提供商客户端 |

**LLMClient 使用**:
```python
class LLMClient:
    def __init__(self, model_config: ModelConfig): ...
    
    def chat(
        self,
        messages: list[LLMMessage],
        model_config: ModelConfig,
        tools: list[Tool] = None,
        reuse_history: bool = True,
    ) -> LLMResponse: ...
```

---

### 6. 轨迹记录器 (`trae_agent/utils/trajectory_recorder.py`)

**职责**: 记录智能体执行的完整轨迹，用于调试和分析。

**记录内容**:
- 任务描述
- LLM 提供商和模型
- 最大步数
- 工具调用
- 执行结果

---

## 关键工作流程

### 任务执行流程

```
1. 用户通过 CLI 输入任务
   ↓
2. 配置加载和解析
   ↓
3. Agent 实例创建
   ↓
4. 新任务初始化 (new_task)
   - 设置系统提示词
   - 初始化工具
   - 开始轨迹记录
   ↓
5. MCP 工具发现和初始化 (initialise_mcp)
   ↓
6. 任务执行循环 (execute_task)
   ├─ LLM 调用
   ├─ 工具调用执行
   ├─ 结果处理
   └─ 检查任务完成
   ↓
7. 轨迹记录 finalize
   ↓
8. 返回结果
```

### 交互模式流程

```
1. CLI 启动交互模式
   ↓
2. 控制台初始化 (simple/rich)
   ↓
3. 用户输入任务
   ↓
4. 执行任务 (同上述流程)
   ↓
5. 显示结果
   ↓
6. 等待下一个输入 (或 exit/quit)
```

---

## 配置文件格式

### YAML 配置（推荐）

```yaml
agents:
  trae_agent:
    enable_lakeview: true
    model: trae_agent_model
    max_steps: 200
    tools:
      - bash
      - str_replace_based_edit_tool
      - sequentialthinking
      - task_done

model_providers:
  anthropic:
    api_key: your_anthropic_api_key
    provider: anthropic
  openai:
    api_key: your_openai_api_key
    provider: openai

models:
  trae_agent_model:
    model_provider: anthropic
    model: claude-sonnet-4-20250514
    max_tokens: 4096
    temperature: 0.5

mcp_servers:
  playwright:
    command: npx
    args:
      - "@playwright/mcp@0.0.27"
```

### 环境变量配置

```bash
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_BASE_URL="your-openai-base-url"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export ANTHROPIC_BASE_URL="your-anthropic-base-url"
export GOOGLE_API_KEY="your-google-api-key"
export GOOGLE_BASE_URL="your-google-base-url"
export OPENROUTER_API_KEY="your-openrouter-api-key"
export OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
export DOUBAO_API_KEY="your-doubao-api-key"
export DOUBAO_BASE_URL="https://ark.cn-beijing.volces.com/api/v3/"
```

---

## 开发和扩展指南

### 添加新工具

1. 在 `trae_agent/tools/` 中创建新工具类，继承自 `Tool`
2. 实现所有抽象方法：`get_name()`, `get_description()`, `get_parameters()`, `execute()`
3. 在 `trae_agent/tools/__init__.py` 的 `tools_registry` 中注册

**示例**:
```python
# trae_agent/tools/my_new_tool.py
from trae_agent.tools.base import Tool, ToolParameter, ToolCallArguments, ToolExecResult

class MyNewTool(Tool):
    def get_name(self) -> str:
        return "my_new_tool"
    
    def get_description(self) -> str:
        return "Description of my new tool"
    
    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="param1",
                type="string",
                description="First parameter"
            )
        ]
    
    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult:
        # Implementation
        param1 = arguments.get("param1")
        return ToolExecResult(output=f"Processed: {param1}")
```

```python
# trae_agent/tools/__init__.py
tools_registry: dict[str, type[Tool]] = {
    # ... existing tools
    "my_new_tool": MyNewTool,
}
```

### 添加新 LLM 提供商

1. 在 `trae_agent/utils/llm_clients/` 中创建新客户端类，继承自 `BaseLLMClient`
2. 在 `LLMProvider` 枚举中添加新项
3. 在 `LLMClient` 的 `__init__` 中添加新 case

---

## 依赖管理

项目使用 `uv` 进行依赖管理，主要依赖包括：

| 依赖 | 用途 |
|------|------|
| `openai` | OpenAI API 客户端 |
| `anthropic` | Anthropic API 客户端 |
| `click` | CLI 框架 |
| `google-genai` | Google Gemini API 客户端 |
| `pydantic` | 数据验证 |
| `rich` | 富文本输出 |
| `pyyaml` | YAML 配置解析 |
| `textual` | 富交互控制台 |
| `mcp` | Model Context Protocol 支持 |
| `tree-sitter` | 代码解析 |

---

## 测试

项目包含完整的测试套件，位于 `tests/` 目录：

- `tests/agent/`: 智能体测试
- `tests/tools/`: 工具测试
- `tests/utils/`: 工具函数测试

**运行测试**:
```bash
uv run pytest
```

---

## 项目运行方式

### 基本使用

1. **安装依赖**:
```bash
git clone https://github.com/bytedance/trae-agent.git
cd trae-agent
uv sync --all-extras
source .venv/bin/activate
```

2. **配置 API 密钥**:
```bash
cp trae_config.yaml.example trae_config.yaml
# 编辑 trae_config.yaml，填入 API 密钥
```

3. **运行任务**:
```bash
trae-cli run "Create a hello world Python script"
```

4. **交互模式**:
```bash
trae-cli interactive
```

### Docker 模式

```bash
# 指定 Docker 镜像
trae-cli run "Your task here" --docker-image python:3.12

# 附加到现有容器
trae-cli run "Your task here" --docker-container-id <container-id>
```

---

## 相关文档

- [项目 README](README.md)
- [工具文档](docs/tools.md)
- [轨迹记录文档](docs/TRAJECTORY_RECORDING.md)
- [路线图](docs/roadmap.md)
- [贡献指南](CONTRIBUTING.md)

---

## 许可证和引用

本项目采用 MIT 许可证。

**引用**:
```bibtex
@article{traeresearchteam2025traeagent,
      title={Trae Agent: An LLM-based Agent for Software Engineering with Test-time Scaling},
      author={Trae Research Team and Pengfei Gao and Zhao Tian and Xiangxin Meng and Xinchen Wang and Ruida Hu and Yuanan Xiao and Yizhou Liu and Zhao Zhang and Junjie Chen and Cuiyun Gao and Yun Lin and Yingfei Xiong and Chao Peng and Xia Liu},
      year={2025},
      eprint={2507.23370},
      archivePrefix={arXiv},
      primaryClass={cs.SE},
      url={https://arxiv.org/abs/2507.23370},
}
```
