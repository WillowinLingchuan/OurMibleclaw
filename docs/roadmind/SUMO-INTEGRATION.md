# 交通疏通决策智能体 RoadMind · SUMO 接入方案

> 从零到「最小闭环」的可执行步骤 —— 每一步都有可直接运行的命令
> 面向：**P2（接入与适配）**、**P3（闭环策略）**、**P1（场景业务参数）** ｜ 资料基于 SUMO 官方文档核对整理
> ℹ️ 人力编号沿用仓库统一口径：**P1 产品业务 / P2 后端架构 / P3 算法 / P4 前端全栈**（见 [`TEAM-ROLES.md`](TEAM-ROLES.md) 第一节）
> ⚠️ 本文解决的是本方向**唯一的命门**：回流闭环到底能不能跑起来

---

## 零、这份文档要交付什么

### 唯一的验收标准

> **一条命令，跑出「智能体改了自己的疏导规则，且第 2 轮比第 1 轮好」的对比数据。**

达成 = 本方向是**智能体**。达不成 = 退化为**调度系统**（作品仍成立，但拿不到最关键的那档分）。

### 为什么必须有它

项目其余部分都是确定性劳动（调 LLM、做看板、写规则库），做得出来是必然的。
**全案唯一需要"证据"的地方，就是闭环。**

### 它在原构想里的位置

原构想第五节「可选进阶加分功能」第 3 条写的是：*「简易交通仿真：随机生成模拟车流数据」*。

**那是最低配。** SUMO 把这一条从「自己写个随机数生成器」升级为「用学术界通用工具」——
答辩时这一句话的含金量，远超工作量之差：

> *"视觉用公开数据集验证，闭环在 SUMO 仿真器里跑 —— 都是学术界在用的成熟工具，**不是自制模拟器**。"*

### 时间预算

| 阶段 | 内容 | 人力 | 天数 |
|---|---|---|---|
| **A** | 安装 + 跑起来看到车 | P2 | 0.5 |
| **B1** | 路网 + 车流生成（纯命令，见第二章前半） | P2 | 0.5 |
| **B2** | 3 套预置场景的**业务参数**设计（参数表见本文第十节） | **P1** | 1.0 |
| **C** | TraCI 接入 + 决策适配层 | P2 | 1.5 |
| **D** | 回流指标口径 + 最小闭环脚本 | P2 + **P3** | 1.5 |
| **E** | 与 Agent 打通 + 可复现验证 | P2 + **P3** | 1 |
| | **合计** | | **约 6 人天（1 周）** |

> **P2 仍是唯一的大头（约占 4–5 人天）。** 这也是**建议 P2 最先动工**的原因（见 [`TEAM-ROLES.md`](TEAM-ROLES.md) 第七节铁律 1）。
> **P3 在 D / E 两阶段必须到位**：`agent.decide()` 是「会不会改主意」的全部所在。

---

## 一、安装（约 30 分钟）

### 1.1 装 SUMO

Windows 用官方 installer：https://sumo.dlr.de/docs/Installing/Windows.html

**必须设环境变量 `SUMO_HOME`** —— 指向安装目录（形如 `C:\Program Files (x86)\Eclipse\Sumo`）。
`traci` 靠它找 `tools` 目录，**不设就 `import` 失败**。

```bash
sumo --version
netgenerate --version
echo $SUMO_HOME
```

### 1.2 装 traci

```bash
pip install traci          # 官方已支持（推荐，独立于 SUMO 安装）
```

或让脚本自己找路径：

```python
import os, sys
if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci
```

### ⚠️ 1.3 路径陷阱（本机必看）

本机 Windows 用户名是 `l'z'l` —— **含单引号**。SUMO 的不少脚本（`randomTrips.py`、部分 `netconvert` 调用）不处理这种路径，会直接崩。

> ### 规矩：所有 SUMO 场景文件一律放 `D:\GIT\` 下，绝不放 `C:\Users\...`

这不是理论风险，是这类工具在 Windows 上最常见的翻车点之一。

---

## 二、造一个「最小世界」（约半天）

### 2.1 路网：一条命令生成 3×3 网格

```bash
cd /d D:\GIT\docs\roadmind\sim
netgenerate --grid --grid.number 3 --grid.length 200 ^
            --default.lanenumber 2 --tls.guess true ^
            -o net.net.xml
```

| 参数 | 作用 |
|---|---|
| `--grid.number 3` | 3×3 路口 —— 够演示"一个路口堵了，邻近路口受影响" |
| `--grid.length 200` | 边长 200 米 |
| `--default.lanenumber 2` | 双向各 2 车道（单车道没法演示"封一条道"） |
| `--tls.guess true` | 让 SUMO 自动在需要处配信号灯 |

> ⚠️ 若跑完发现路口没有信号灯：把路口 ID 传给 `--tls.set`，或手写 `.nod.xml` 把节点标 `type="traffic_light"`。
> 先跑 `netgenerate --grid ... -o net.net.xml`，再用 `sumo-gui` 打开看一眼 —— **别等到写代码时才发现没灯。**

### 2.2 车流：用官方工具生成

```bash
python "%SUMO_HOME%\tools\randomTrips.py" -n net.net.xml -e 3600 -p 2 ^
       --fringe-factor max ^
       -o trips.trips.xml
```

| 参数 | 作用 |
|---|---|
| `-e 3600` | 仿真到 3600 秒（1 小时） |
| `-p 2` | 每 2 秒插入一辆车 |
| `--fringe-factor max` | 车一律从路网**边缘**进、边缘出 ← **别让车在网格内部凭空出现**，否则不像真实过境交通 |

> ★ **同一组参数重复跑，结果完全一致** —— 这是可复现性的基础，答辩时是硬通货。
> 想模拟早晚高峰？用多段 period：`-p "1.0,0.5,2.0"`，把时段切段、各段不同到达率。

### 2.3 配置文件：把三样东西绑起来

新建 `demo.sumocfg`：

```xml
<configuration>
    <input>
        <net-file   value="net.net.xml"/>
        <route-files value="trips.trips.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end   value="3600"/>
    </time>
    <output>
        <tripinfo-output value="tripinfo.xml"/>
    </output>
    <processing>
        <time-to-teleport value="-1"/>
    </processing>
</configuration>
```

> ### ★ `time-to-teleport = -1` 这一行必须加
> 默认情况下，SUMO 会把堵太久的车**直接传送走**。你辛苦造的拥堵实验，会被悄无声息地抹平。
> **这是新手最容易踩、也最难自己发现的坑。**

### 2.4 验收

```bash
sumo-gui -c demo.sumocfg
```

看到车在跑、红绿灯在变 → **阶段 B 完成**。

---

## 三、接上 Python：TraCI 生命周期（约半天）

TraCI 是外部程序在仿真运行中**实时读状态、下指令**的接口。**它就是 Agent 的手。**

### 3.1 最小脚本

```python
import os, sys
if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

traci.start(["sumo-gui", "-c", "demo.sumocfg"])   # 演示用 sumo-gui；批量实验用 sumo

step = 0
while step < 1000:
    traci.simulationStep()      # 推进一个仿真步（默认 1 秒）
    # —— 这里就是 Agent 插手的地方 ——
    step += 1

traci.close()
```

### 3.2 三个必须知道的点

| 点 | 说明 |
|---|---|
| **sumo vs sumo-gui** | 演示用 `sumo-gui`（能录屏、能看车流）；跑 20 轮对照实验用 `sumo`（无界面，**快 5-10 倍**） |
| **推进方式** | `traci.simulationStep()` 每次 1 步；也可传参一步跑到指定时刻 |
| **多实例** | `traci.start([...], label="sim1")` + `traci.switch("sim1")` —— **做"有智能体 vs 无智能体"对照实验就靠这个** |

---

## 四、★ 核心：把 Agent 的决策翻译成 TraCI

这是全案的**接缝**，也是最容易出问题的地方。

### 4.1 原则：Agent 不许直接写 TraCI

> ### LLM 只输出结构化决策（JSON），由一层**确定的适配器**翻译成 TraCI 调用。

这是「幻觉抑制三道防线」里的**架构隔离**。
让 LLM 直接生成代码或直接调 API，它一定会编出不存在的函数、不存在的路口 ID。

### 4.2 决策 → TraCI 映射表

| Agent 决策（JSON） | TraCI 调用 | 用途 |
|---|---|---|
| `{"action":"extend_green","tls":"J2","seconds":15}` | `trafficlight.setPhaseDuration("J2", 15)` | 主干道延长绿灯泄流 |
| `{"action":"set_phase","tls":"J2","index":2}` | `trafficlight.setPhase("J2", 2)` | 切到预置相位 |
| `{"action":"set_state","tls":"J2","state":"GGrr"}` | `trafficlight.setRedYellowGreenState("J2","GGrr")` | 完全自定义配时 |
| `{"action":"ban_lane","lane":"edge1_0"}` | `lane.setDisallowed("edge1_0", ["passenger"])` | 封道 |
| `{"action":"reroute","percent":30}` | 逐车调用 `vehicle.rerouteTraveltime(vehID)` | 诱导分流 |
| `{"action":"incident","edge":"edge1","lane":0}` | 在该位置插入一辆 `speed=0` 的车 | 注入事故 / 抛锚 |

### 4.3 状态串怎么写

`setRedYellowGreenState` 的第二个参数是一个**字符串**，每个字符对应一条受控车道（顺序由路网决定）：

| 字符 | 含义 |
|---|---|
| `G` | 绿灯（允许通行） |
| `g` | 绿灯，但该流向**需让行 / 减速** |
| `y` / `Y` | 黄灯（`y` 为减速黄灯） |
| `r` / `R` | 红灯（`r` 为减速红灯） |
| `o` / `O` | 关闭 |

**先读后写** —— 车道顺序**不能猜**：

```python
tls = "J2"
links = traci.trafficlight.getControlledLinks(tls)        # 看有几条受控连接
state = traci.trafficlight.getRedYellowGreenState(tls)    # 看当前状态串
print(len(links), len(state), state)                      # 串长必须 == 连接数
```

**状态串长度必须等于受控连接数**，多一个少一个都报错。

### 4.4 ⚠️ 三个必踩的坑

| 坑 | 后果 | 对策 |
|---|---|---|
| **红灯"瞬间"变绿** | 仿真里车瞬移 / 报碰撞 | 必须经过黄灯相位。**用 `setPhase` 切预置相位，别用自定义串跳过黄灯** |
| **混用 `setPhase` 与 `setRedYellowGreenState`** | 自定义状态会把程序 ID 改成 `online`，之后 `setPhase` 的 index 语义就乱了 | **二选一**：要么全程预置相位，要么全程自定义串 |
| **相位时长设为 0 或极短** | 红绿灯高频闪烁，仿真失真 | 设下界，如 `max(seconds, 5)` |

### 4.5 护栏（必须写进 Agent 的 prompt）

```
可用路口 ID: J0..J8            ← 从 traci.trafficlight.getIDList() 动态注入
绿灯时长范围: 5-60 秒
禁止: 同一路口 10 秒内重复调整
禁止: 自定义状态串（只允许 setPhase）
```

> ### ★ 路口 ID 必须动态注入，不能写死
> 让 LLM 猜 ID 是幻觉重灾区 —— 它会自信地输出一个不存在的 `J12`。

---

## 五、★ 回流指标怎么取

闭环的"结果"必须是一个**数字**，Agent 才可能据此改策略。

### 5.1 用 tripinfo（离线，最准）

配置里加 `tripinfo-output` 后，仿真结束会写出每辆车一条记录：

```xml
<tripinfo id="veh_12" depart="34.00" arrival="121.00"
          duration="87.00" routeLength="1240.00"
          waitingTime="12.00" timeLoss="41.00" departDelay="0.00"/>
```

| 字段 | 含义 | 用途 |
|---|---|---|
| **`duration`** | 全程行程时间 | ★ **主指标** —— 疏通有效 = 它下降 |
| **`timeLoss`** | 因堵车 / 路口等损失的时间 | 更"纯"的拥堵指标，**建议同时报** |
| `waitingTime` | 完全静止等待的时间 | 反映排队严重度 |
| `departDelay` | 想出发却挤不进路网而等待的时间 | 反映路网是否已饱和 |

Python 侧用 `xml.etree.ElementTree` 解析 `tripinfo.xml`，取平均。

### 5.2 在线指标（实时，用于看板）

```python
traci.edge.getLastStepMeanSpeed(edgeID)       # 该路段平均速度
traci.edge.getLastStepHaltingNumber(edgeID)   # 该路段停着不动的车数 ← 排队长度
traci.vehicle.getTimeLoss(vehID)              # 单车累计损失时间
```

### 5.3 输出：喂回给 Agent 的凭证

```json
{
  "round": 3,
  "rule_version": "v3",
  "metrics": {
    "mean_duration": 118.4,
    "mean_timeloss": 52.1,
    "mean_waiting": 18.7,
    "halting_max": 23
  },
  "delta_vs_last_round": { "mean_duration": -9.3 }
}
```

> **`delta_vs_last_round` 就是"闭环存在"的证明。** 有了它，Agent 才可能改主意。

---

## 六、★ 最小闭环脚本（可直接改成真代码）

```python
import os, sys, json
if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci
import xml.etree.ElementTree as ET

TLS      = "J2"        # 演示聚焦一个路口
ROUNDS   = 5
SIM_END  = 1800


def run_round(rule, round_no, gui=False):
    """按 rule 跑一轮仿真，返回指标"""
    binary = "sumo-gui" if gui else "sumo"
    traci.start([binary, "-c", "demo.sumocfg",
                 "--end", str(SIM_END),
                 "--tripinfo-output", f"tripinfo_r{round_no}.xml",
                 "--seed", "42"])            # ★ 固定种子 = 可复现
    try:
        while traci.simulation.getTime() < SIM_END:
            traci.simulationStep()

            # —— 每 60 秒，按当前规则调整一次配时 ——
            if int(traci.simulation.getTime()) % 60 == 0:
                phase = rule["green_phase_index"]
                if traci.trafficlight.getPhase(TLS) != phase:
                    traci.trafficlight.setPhase(TLS, phase)
                    traci.trafficlight.setPhaseDuration(
                        TLS, max(rule["green_seconds"], 5))   # ★ 下界护栏
    finally:
        traci.close()

    # —— 收指标 ——
    durs, losses, waits = [], [], []
    for t in ET.parse(f"tripinfo_r{round_no}.xml").getroot():
        durs.append(float(t.get("duration")))
        losses.append(float(t.get("timeLoss")))
        waits.append(float(t.get("waitingTime")))
    n = max(len(durs), 1)
    return {"rule_version":   rule["version"],
            "mean_duration":  sum(durs)   / n,
            "mean_timeloss":  sum(losses) / n,
            "mean_waiting":   sum(waits)  / n}


# ================= 闭环 =================
current_rule = {"version": "v0", "green_phase_index": 0, "green_seconds": 30}
history = []

for r in range(1, ROUNDS + 1):
    metrics = run_round(current_rule, r, gui=False)
    history.append(metrics)

    prev  = None if r == 1 else history[-2]["mean_duration"]
    delta = None if prev is None else metrics["mean_duration"] - prev

    print(f"[Round {r}] rule={current_rule['version']} "
          f"duration={metrics['mean_duration']:.1f} delta={delta}")

    # ★★ 这里换成你的 Agent：把 history 喂给它，让它输出 next_rule ★★
    # next_rule = agent.decide(history)     # ← LLM 只输出 JSON，绝不碰 TraCI
    next_rule = {"version": f"v{r}",
                 "green_phase_index": 1,                 # 占位：第一版先用规则/网格搜索
                 "green_seconds": 30 + 5 * r}

    if next_rule == current_rule:
        print("⚠️ 规则未变化 —— 闭环没起作用，检查 Agent")
        break
    current_rule = next_rule

json.dump(history, open("loop_history.json", "w"), ensure_ascii=False, indent=2)
```

> ### ★ 先用"假 Agent"把管道跑通，再换成真 LLM
> 上面那段写死的 `next_rule` 不是偷懒，是**必要的调试顺序**。
> 否则你分不清"闭环没效果"是管道坏了还是 Prompt 不好 —— **这个顺序颠倒会白白浪费好几天。**

---

## 七、验收清单（跑完 = 本方向是智能体）

- [ ] `sumo --version` 与 `echo $SUMO_HOME` 都正常
- [ ] `sumo-gui -c demo.sumocfg` 能看到车流与红绿灯
- [ ] 能读到某路口的当前相位与状态串
- [ ] 能改配时，并观察到 `duration` **发生变化**（**哪怕变差也算打通**）
- [ ] 能注入一次事故，并观察到排队（`halting_number` 上升）
- [ ] 跑完 5 轮，`loop_history.json` 里 **rule_version 在变，且 duration 有下降趋势**
- [ ] 固定 seed 重跑一次，结果一致

**前 5 项 = 闭环打通**（这是命门）。**后 2 项 = 可写进报告的证据。**

---

## 八、坑与对策

| 坑 | 症状 | 对策 |
|---|---|---|
| **路径含 `'`** | 各种脚本莫名崩溃 | 场景文件一律放 `D:\GIT\...`（见 1.3） |
| `SUMO_HOME` 未设 | `import traci` 失败 | 设环境变量后**重开终端** |
| **车轮瞬移** | 堵死的车自己消失了，实验白做 | `time-to-teleport = -1`（见 2.3） |
| 状态串长度错 | 直接报错 | 先 `getControlledLinks` 再写（见 4.3） |
| 端口占用 | 多实例启动失败 | `from sumolib.miscutils import getFreeSocketPort` |
| sumo-gui 太慢 | 演示卡顿 | `--delay 100` 加速；演示只放 30 秒，其余用 `sumo` |
| 结果不可复现 | 两轮对比失去意义 | **固定 `--seed`**，每次实验都记录 |

---

## 九、退路

| 情况 | 降级方案 | 代价 |
|---|---|---|
| SUMO 装不上 / 一周跑不通 | 换 **CityFlow**（更轻，专为 RL 设计） | 生态小，但 API 更简单 |
| 装得上但 TraCI 接不通 | **离线回放**：预生成若干 tripinfo，Agent 在数据上迭代 | 失去"实时控制"的演示效果 |
| 完全跑不通 | 退化为普通调度系统 | **作品仍成立**，只是拿不到"这是智能体"那档分 |

> ⚠️ 上述降级**都不致命** —— 符合团队决策标准：**硬核部分是可选的，不是承重的。**

---

## 十、分工落点

| 人 | 做什么 |
|---|---|
| **P2 · 后端 / 架构** | 第一章（安装）、第二章前半（路网 + 车流生成）、第三章（TraCI）、**第四章（决策适配层）**、第六章（闭环脚本工程）、第七章验收自测 |
| **P3 · 算法 / 核心智能** | **第五章（回流指标口径 = 评测指标的定义）**、第六章的 `agent.decide()` —— 把 `history` 变成 `next_rule` 的策略 |
| **P1 · 产品 + 交通业务** | 第二章后半（3 套预置场景的**业务参数**，对应 [`DEMO-SCRIPT.md`](DEMO-SCRIPT.md) 的三个场景）；答辩话术：*"闭环在 SUMO 仿真器中验证，这是学术界通用工具，不是自制模拟器。"* |
| **P4 · 前端 / 全栈** | **消费**第六章跑出的对比数据 → 大屏「复盘前后对比视图」（见 [`TEAM-ROLES.md`](TEAM-ROLES.md) P4 交付物 ④） |

### 三套预置场景（对应原构想第七节的三个演示案例）

| 场景 | 在 SUMO 里怎么造 |
|---|---|
| **雨天追尾剐蹭** | 车流加密 + 在 J2 注入 `speed=0` 的车 + `setPhase` 延长绿灯 |
| **车辆抛锚占道** | 封一条车道（`lane.setDisallowed`）+ 观察 `halting_number` 上升 + 诱导分流 |
| **大雾出行** | 全局限速下调（`edge.setMaxSpeed`）+ 对比有 / 无智能体的行程时间 |

> ★ 场景 2（抛锚占道）是**全场最重要的演示** —— 它是唯一能展示"规则被改写"的场景。
> 详见 [`DEMO-SCRIPT.md`](DEMO-SCRIPT.md)。

---

## 附：命令速查

```bash
# 装完验证
sumo --version
netgenerate --version

# 造路网（3x3 网格，200m 边长，双向 2 车道，自动配信号灯）
netgenerate --grid --grid.number 3 --grid.length 200 \
            --default.lanenumber 2 --tls.guess true -o net.net.xml

# 造车流（1 小时，每 2 秒一辆，边缘进出）
python "%SUMO_HOME%\tools\randomTrips.py" -n net.net.xml -e 3600 -p 2 \
       --fringe-factor max -o trips.trips.xml

# 跑
sumo-gui -c demo.sumocfg      # 演示
sumo     -c demo.sumocfg      # 批量实验

# 固定种子复现
sumo -c demo.sumocfg --seed 42 --tripinfo-output tripinfo.xml
```

```python
# 常用 TraCI
traci.start(["sumo", "-c", "demo.sumocfg"])
traci.simulationStep()
traci.simulation.getTime()
traci.trafficlight.getIDList()
traci.trafficlight.getPhase("J2")
traci.trafficlight.getRedYellowGreenState("J2")
traci.trafficlight.setPhase("J2", 1)
traci.trafficlight.setPhaseDuration("J2", 30)
traci.edge.getLastStepMeanSpeed("edge1")
traci.edge.getLastStepHaltingNumber("edge1")
traci.close()
```

---

*本文基于 SUMO 官方文档核对整理：[TraCI4Traffic Lights](https://sumo.dlr.de/userdoc/Tutorials/TraCI4Traffic_Lights.html)、[Interfacing TraCI from Python](https://sumo.dlr.de/userdoc/TraCI/Interfacing_TraCI_from_Python.html)、[Change Traffic Lights State](https://sumo.dlr.de/userdoc/TraCI/Change_Traffic_Lights_State.html)、[netgenerate](https://sumo.dlr.de/userdoc/netgenerate.html)、[TripInfo Output](https://sumo.dlr.de/userdoc/Simulation/Output/TripInfo.html)、[randomTrips.py](https://sumo.dlr.de/userdoc/Tools/Trip.html)*
*配套：[`EXECUTION-PLAN.md`](EXECUTION-PLAN.md)（方案）· [`TEAM-ROLES.md`](TEAM-ROLES.md)（分工与排期）· [`ARCHITECTURE.md`](ARCHITECTURE.md)（智能体角色）· [`DEMO-SCRIPT.md`](DEMO-SCRIPT.md)（演示脚本）*
