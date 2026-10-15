"""图18 单帧车辆、导弹数据各折检出情况（按表格数据更新）。"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

FOLDS = ["第1折", "第2折", "第3折", "第4折"]

# 标注目标数：取自表格
GT_HIGH = [113, 119, 118, 105]      # SNR>3
GT_LOW = [1678, 1181, 1256, 918]    # SNR≤3

# TP：第2折取自表17，第1、3、4折为原图实测值
TP_HIGH = [110, 115, 115, 101]
TP_LOW = [1545, 988, 1139, 814]

C_TP, C_FN = "#6fa0d0", "#f4b183"
E_TP, E_FN = "#3f6f9f", "#c9773f"


def draw(ax, tp, gt, title, ylim, yticks):
    fn = [g - t for g, t in zip(gt, tp)]
    x = range(len(FOLDS))
    ax.bar(x, tp, width=0.55, color=C_TP, edgecolor=E_TP, linewidth=0.8, label="TP")
    ax.bar(x, fn, width=0.55, bottom=tp, color=C_FN, edgecolor=E_FN, linewidth=0.8, label="FN")
    for i, (t, g) in enumerate(zip(tp, gt)):
        ax.text(i, g + ylim * 0.012, f"{t}/{g}", ha="center", va="bottom", fontsize=10)
    ax.set_title(title, fontsize=11)
    ax.set_xticks(list(x))
    ax.set_xticklabels(FOLDS, fontsize=11)
    ax.set_ylim(0, ylim)
    ax.set_yticks(yticks)
    ax.tick_params(axis="y", labelsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=10, loc="upper right")


fig, axes = plt.subplots(1, 2, figsize=(10, 3.9))
draw(axes[0], TP_HIGH, GT_HIGH, "单帧车辆、导弹（SNR>3）", 140, range(0, 121, 20))
draw(axes[1], TP_LOW, GT_LOW, "单帧车辆、导弹（SNR≤3）", 1950, range(0, 1751, 250))
fig.text(0.5, 0.015, "柱顶数字：TP / 标注目标数；各折FP均为0", ha="center", fontsize=9, color="#555555")
fig.tight_layout(rect=(0, 0.05, 1, 1), w_pad=4)
fig.savefig("fig18.png", dpi=300)
print("saved fig18.png")
