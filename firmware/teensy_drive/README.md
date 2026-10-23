# Teensy drive prototype / Teensy 驱动原型

**Status: desktop-tested prototype with a dry-run output backend. It cannot drive
motors. Do not mark the parent issue or wheel bench test complete.**

本目录提供 C++ 安全控制核心、USB 消息解析、电脑端测试、Teensy 4.1
编译入口和 Python 协议编码器。电机控制模式、接线和会话协议尚未确认，
因此 `src/main.cpp` 仅保存目标值，不设置或写入任何电机引脚。
这不是用于已连接电机的可部署固件：高阻引脚不代表控制器必然关闭。

## 在 Ubuntu 24.04 / WSL 使用

在正式 Git 仓库根目录运行以下命令。只需首次安装工具；不要在 Jetson 上安装。

```bash
sudo apt update
sudo apt install python3-venv build-essential
python3 -m venv ~/.venvs/innex-pio
source ~/.venvs/innex-pio/bin/activate
python -m pip install platformio==6.1.18
cd firmware/teensy_drive
```

1. 不接开发板，运行 C++ 测试：

```bash
pio test -e native
```

2. 测试 Jetson 端的协议编码工具：

```bash
python -m unittest discover -s tools -p 'test_*.py' -v
python tools/protocol.py 1 0 0
```

第二条只显示 18 字节的十六进制消息，不连接串口，也不发送电机命令。
预期：`44 52 01 00 01 00 00 00 00 00 00 00 00 00 00 00 be 37`。

3. 编译 Teensy 固件（不刷写）：

```bash
pio run -e teensy41
```

成功后产物位于 `.pio/build/teensy41/firmware.hex`。**编译成功不代表真实电机可用。**
没有提供自动上传或真实串口发送命令。PlatformIO 首次运行会下载工具链。

## 文件与阅读顺序

| 文件 | 用途 |
|---|---|
| `PROTOCOL.md` | INX-140 两端需要共同审核的协议草案和已知限制 |
| `lib/DriveCore/DriveCore.h` | 公开接口、250 ms 超时和原型目标值范围 |
| `lib/DriveCore/DriveCore.cpp` | CRC、解析、序号比较、归零与重新使能逻辑 |
| `test/test_drive_core/test_main.cpp` | 无硬件的安全行为测试 |
| `src/main.cpp` | Arduino setup/loop、每轮有界读取、无电机输出的适配层 |
| `tools/protocol.py` | 与固件配套的 Python 主机编码器，不是 ROS 节点 |
| `tools/test_protocol.py` | Python 编码器测试 |
| `platformio.ini` | 固定 Native 1.2.1、Teensy 5.0.0 的构建配置 |

逻辑：开机停 → 新的零命令使能 → 新的运动命令设置目标 →
250 ms 没有新有效命令则停并解除使能 → 必须重新发送新的零命令。
旧消息和重复消息不刷新计时；损坏或越界消息立即停止。
核心不包含 Arduino API，因此测试和实际固件使用同一份实现。

## 下一步与验收

- 与 INX-140 负责人共同确认协议；Python 编码器仅是集成起点，尚无 ROS 桥接。
- 增加会话/新鲜度握手，防止重启后旧队列指令被接受；详见 PROTOCOL.md。
- 确认 Sabertooth 控制模式、引脚、电气默认停止状态、编码器和速度闭环。
- 用真正的控制器适配层替换 DryRunOutput，停止路径必须实际关闭全部驱动输出。
- 测量最坏循环延迟、串口积压、输出停止延迟，并满足端到端 250 ms 要求。
- 桥接端还必须实现其独立的 500 ms 超时，本目录不实现该 ROS 节点。
- 在 Ubuntu 工作区运行 `colcon build`、`colcon test` 和 `colcon test-result --verbose`。
- 硬件测试前按 AGENTS.md 和 docs/safety.md 由现场人员确认急停、架空与固定时长。
  测试结束发零；刷写必须有人明确要求且在场。本次没有刷写或控制电机。

不要直接推送 main。将这些文件加入任务分支，提交 PR。

## 已核对的上游资料

- [PlatformIO Core 6.1.18](https://github.com/platformio/platformio-core/releases/tag/v6.1.18)
- [Teensy 平台 5.0.0 / Teensyduino 1.59](https://github.com/platformio/platform-teensy/releases/tag/v5.0.0)
- [Native 平台 1.2.1](https://github.com/platformio/platform-native/releases/tag/v1.2.1)
- [共享核心放入 lib 目录](https://docs.platformio.org/en/stable/advanced/unit-testing/structure/shared-code.html)
- [Teensy USB Serial API](https://www.pjrc.com/teensy/td_serial.html)

PJRC 说明 USB Serial 在 setup 前初始化，Serial.begin() 不是必需的；
本入口不等待主机连接，不使用 delay、阻塞读取或应用层动态分配。
