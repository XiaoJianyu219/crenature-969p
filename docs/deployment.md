# 展出装置部署手册

从零搭起"观众靠近 → 屏幕开始生长花朵"的整套装置。
下文 IP、用户名都是示例，换成你自己的。

```
PIR 传感器 ──GPIO17──▶ Raspberry Pi 4B ──SSH(密钥)──▶ Windows 迷你主机 ──任务计划程序──▶ 全屏动画 ──HDMI──▶ 显示器
```

分工：画面由 Windows 迷你主机（我们用的是 GMKtec）渲染，树莓派只做"感知 + 发指令"。

## 1. 硬件清单

| 物品 | 备注 |
|---|---|
| Raspberry Pi 4 Model B | 16/32 GB 的 micro SD 卡即可 |
| 5V 3A USB-C 电源 | 最好用树莓派官方电源；**超过 5V 可能烧坏树莓派** |
| PIR 人体红外传感器 + 3 根杜邦线 | 带电位器的型号可以调灵敏度和保持时间 |
| Windows 迷你主机 + HDMI 显示器 | 运行动画 |
| 路由器 | 不需要连外网，只要树莓派和主机在同一局域网；5 GHz 更稳 |
| micro HDMI 转 HDMI 线 | 仅首次配置树莓派网络时用 |

## 2. 树莓派系统

1. 用 Raspberry Pi Imager 烧录 Raspberry Pi OS（32/64 位均可）。在自定义设置里：
   设定主机名和用户名/密码，**在 Remote access 中打开 SSH（密码登录）**。
2. 首次开机接显示器，连上局域网，在网络图标 → Advanced Options → Connection Information
   里记下树莓派 IP（例：`192.168.0.17`）。在烧录时预配 Wi-Fi 我们多次没成功，接屏配置最省事。
3. `sudo raspi-config` → Interface Options，确认 SSH（需要远程桌面再开 VNC），然后 `sudo reboot`。
4. 之后就可以在笔记本上 `ssh <用户名>@192.168.0.17` 操作，或用 RealVNC Viewer 看树莓派桌面，
   树莓派不再需要显示器。

## 3. 传感器接线

展出时实际使用的接线：

| 传感器引脚 | 树莓派物理引脚 | 含义 |
|---|---|---|
| VCC | 17 | 3.3V 供电 |
| OUT | 11 | GPIO17（BCM 编号，脚本默认值） |
| GND | 9 | 地 |

> 换用其他传感器前先看它的供电范围：HC-SR501 这类模块标称 4.5V 以上，3.3V 下不稳定时改接
> 2 号脚（5V）；它的 OUT 仍是 3.3V 电平，可以直接接 GPIO。

## 4. Windows 主机：运行环境

```powershell
git clone https://github.com/XiaoJianyu219/crenature-969p.git C:\crenature-969p
cd C:\crenature-969p
python -m pip install -r requirements.txt
python -m crenature --windowed --duration 20      # 先确认动画能在窗口里跑
```

记下 `ipconfig` 里主机的局域网 IP（例：`192.168.0.14`）。

## 5. Windows 主机：开启 SSH 服务器

管理员 PowerShell：

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service sshd -StartupType Automatic
```

在树莓派上测试能用密码登录：`ssh "<Windows用户名>"@192.168.0.14`（用户名有空格时要加引号）。

## 6. 免密登录（传感器自动触发的前提）

树莓派上生成密钥（**不要设 passphrase**，否则无人值守时会卡住）：

```bash
ssh-keygen -t ed25519
cat ~/.ssh/id_ed25519.pub        # 复制输出的这一行
```

把这行公钥放到 Windows 上的哪个文件，取决于登录用的账户是不是管理员：

| Windows 账户 | 公钥文件 |
|---|---|
| 普通用户 | `C:\Users\<用户名>\.ssh\authorized_keys` |
| **管理员组成员** | **`C:\ProgramData\ssh\administrators_authorized_keys`** |

我们在这一步反复测试了很久：公钥写进用户目录的 `authorized_keys` 后仍然要求输密码。
原因是 Windows 自带的 `sshd_config` 末尾有 `Match Group administrators` 段，
**管理员账户只读 `administrators_authorized_keys`**，用户目录下的文件被忽略。

管理员账户的做法（管理员 PowerShell，文件不能带 `.txt` 后缀；`ProgramData` 是隐藏文件夹）：

```powershell
notepad C:\ProgramData\ssh\administrators_authorized_keys   # 粘贴公钥并保存
icacls C:\ProgramData\ssh\administrators_authorized_keys /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"
Restart-Service sshd
```

权限必须只留 Administrators 和 SYSTEM，否则 sshd 会拒绝这个文件。
回到树莓派验证，不再询问密码即成功：

```bash
ssh -o BatchMode=yes "<Windows用户名>"@192.168.0.14 "echo ok"
```

## 7. 让动画出现在屏幕上：任务计划程序

通过 SSH 直接启动的程序运行在 sshd 的非交互会话里，**窗口不会出现在显示器上**。
我们最初让树莓派经 SSH 直接运行 Python 没有成功，改为下面的做法：树莓派不直接运行 Python，而是让 Windows 执行一个"只在用户登录时运行"的计划任务，
由它在已登录的桌面里打开全屏窗口。

在 Windows 上（普通 PowerShell 即可）：

```powershell
powershell -ExecutionPolicy Bypass -File C:\crenature-969p\windows\register_task.ps1
schtasks /run /tn "crenature"     # 本机测试：应当弹出全屏动画
```

- `run_crenature.bat` 从仓库根目录启动 `python -m crenature`，输出写进 `windows\crenature.log`，
  出问题先看这个日志。如果计划任务里找不到 `python`，设置环境变量 `CRENATURE_PYTHON` 为 `python.exe` 的完整路径。
- 任务设置了"已在运行则忽略新请求"：一段动画没放完时再有人经过，不会叠出第二个窗口。
- 加 `-AtLogOn` 参数可以让主机开机登录后自动先播一遍。
- 主机需要设置为自动登录并关闭睡眠，否则计划任务找不到可显示的桌面。

## 8. 树莓派：传感器脚本

```bash
sudo apt update && sudo apt install -y python3-gpiozero git
git clone https://github.com/XiaoJianyu219/crenature-969p.git ~/crenature-969p
cd ~/crenature-969p/pi

# 先不接传感器，按回车模拟有人经过，确认 SSH 链路
python3 sensor_trigger.py --host 192.168.0.14 --user "<Windows用户名>" --dry-run

# 接上传感器正式运行
python3 sensor_trigger.py --host 192.168.0.14 --user "<Windows用户名>"
```

终端显示 `Ready` 后在传感器前挥手，应看到 `motion detected -> starting task` 和 `exit code 0: SUCCESS ...`，
同时主机屏幕开始播放。两次触发之间默认冷却 10 秒（`--cooldown`）。

开机自启：编辑 `pi/crenature-sensor.service` 里的用户和三个环境变量，然后

```bash
sudo cp crenature-sensor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now crenature-sensor
journalctl -u crenature-sensor -f
```

## 9. 排障

| 现象 | 检查 |
|---|---|
| 树莓派 `ssh` 仍要密码 / `Permission denied (publickey)` | 账户是否为管理员（见第 6 步）；`administrators_authorized_keys` 权限；文件是否被存成了 `.txt` |
| `exit code 0` 但屏幕没反应 | 主机是否已登录桌面；计划任务是否为"只在用户登录时运行"；看 `windows\crenature.log` |
| 日志里 `python` 不是内部或外部命令 | 设置 `CRENATURE_PYTHON` 为完整路径 |
| 没人也频繁触发 / 有人不触发 | 调传感器上的灵敏度与保持时间电位器；加大 `--cooldown` |
| 动画卡顿 | 降低背景点数，例如 `run_crenature.bat --dots 50000` |
| 树莓派脚本报编码错误 | 源码注释保持纯 ASCII（我们用的系统镜像遇到非 ASCII 注释会报错） |
