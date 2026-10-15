"""图2-4 单帧数据各折测试集目标数量分布（按表格数据更新）。"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

FOLDS = ["第1折", "第2折", "第3折", "第4折"]

# 各折目标数：取自表格（SNR>3、SNR≤3；全部 = 两者之和）
VEHICLE_HIGH = [113, 119, 118, 105]
VEHICLE_LOW = [1678, 1181, 1256, 918]
AIRCRAFT_HIGH = [162, 127, 147, 134]
AIRCRAFT_LOW = [195, 147, 135, 167]

C_LOW, C_HIGH, EDGE = "#a9c6e8", "#3b6fa8", "#2f4f75"


def draw(ax, high, low, title, ylim, yticks):
    total = [h + l for h, l in zip(high, low)]
    x = range(len(FOLDS))
    ax.bar(x, low, width=0.55, color=C_LOW, edgecolor=EDGE, linewidth=0.8, label="SNR≤3")
    ax.bar(x, high, width=0.55, bottom=low, color=C_HIGH, edgecolor=EDGE, linewidth=0.8, label="SNR>3")
    for i, (h, t) in enumerate(zip(high, total)):
        ax.text(i, t + ylim * 0.005, f"{h} / {t}", ha="center", va="bottom", fontsize=10)
    ax.set_title(title, fontsize=11)
    ax.set_xticks(list(x))
    ax.set_xticklabels(FOLDS, fontsize=11)
    ax.set_ylim(0, ylim)
    ax.set_yticks(yticks)
    ax.tick_params(axis="y", labelsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=10, loc="upper right")


fig, axes = plt.subplots(1, 2, figsize=(10, 3.9))
draw(axes[0], VEHICLE_HIGH, VEHICLE_LOW, "单帧车辆、导弹（标注目标数 = TP + FN）", 1880, range(0, 1751, 250))
draw(axes[1], AIRCRAFT_HIGH, AIRCRAFT_LOW, "单帧飞机、雷达（标注目标数 = TP + FN）", 415, range(0, 351, 50))
fig.text(0.5, 0.015, "柱顶数字：SNR>3 目标数 / 全部目标数", ha="center", fontsize=9, color="#555555")
fig.tight_layout(rect=(0, 0.05, 1, 1), w_pad=4)
fig.savefig("fig2-4.png", dpi=300)
print("saved fig2-4.png")
