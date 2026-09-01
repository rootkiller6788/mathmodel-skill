# 机器学习算法说明文档

## 概述

机器学习算法是数学建模中的重要工具，用于从数据中学习模式并进行预测、分类和聚类。本章节涵盖监督分类（逻辑回归、决策树、KNN、朴素贝叶斯、SVM）、集成学习（随机森林、AdaBoost）和异常检测（孤立森林）等常用机器学习算法。

**阅读指引**：本章聚焦**监督分类**视角。相关但不同视角的算法见其他章节——

- **线性回归 / 逻辑回归的关系**：连续值回归用 `02-预测类算法说明.md` §3；分类问题用本章 §1
- **SVM 回归（SVR）**：见 `02-预测类算法说明.md` §5；本章 §5 是 SVM 分类（SVC）
- **XGBoost / LightGBM 预测**：见 `02-预测类算法说明.md` §9；与本章 §7 AdaBoost 同属提升方法，但实现与调参独立
- **聚类分析（K-Means / 层次聚类 / DBSCAN）**：见 `05-统计分析与数据处理算法说明.md` §2，是无监督学习，与本章 KNN 等监督分类不同
- **主成分分析 PCA**：见 `05-统计分析与数据处理算法说明.md` §4，常用于分类前的降维

**运行效率说明**：经典分类器（逻辑回归、朴素贝叶斯、决策树、KNN）在竞赛数据规模（通常 ≤10⁵ 样本、≤10² 特征）下训练耗时秒级；SVM（RBF 核）在中等规模也仅数秒至数十秒。真正耗时的是深度网络和超大规模集成，72 小时竞赛中较少使用。因此机器学习算法可作为常规工具放心选用。

---

## 1. 逻辑回归 (Logistic Regression)

### 算法介绍

逻辑回归是一种广义线性分类模型，尽管名字带"回归"，实际用于**二分类与多分类**。它在线性组合后接 sigmoid 激活，输出样本属于正类的概率，是竞赛中性价比最高的基线分类器之一。

#### 1.1 基本原理

**线性组合**：
$$
z = w^T x + b
$$

**sigmoid 函数**（把实数映射到 (0,1)）：
$$
\sigma(z) = \frac{1}{1 + e^{-z}}
$$

**分类概率**：
$$
P(y=1|x) = \sigma(w^T x + b) = \frac{1}{1 + e^{-(w^T x + b)}}
$$

**决策规则**：$P(y=1|x) \geq 0.5$ 判为正类，否则判为负类。决策边界是超平面 $w^T x + b = 0$。

**损失函数**（负对数似然 / 交叉熵，对单样本）：
$$
L = -[y \log \hat{p} + (1-y) \log(1-\hat{p})]
$$

**带正则化的目标**（L2 时）：
$$
J(w) = -\frac{1}{n}\sum_{i=1}^{n}\left[ y_i \log \hat{p}_i + (1-y_i) \log(1-\hat{p}_i) \right] + \frac{\lambda}{2}\|w\|^2
$$

**多分类扩展**：一对多（OvR，每类训一个二分类器）或 Softmax 回归（直接输出各类概率）。

#### 1.2 使用条件与常见坑

| 条件/坑 | 说明 | 应对 |
|---------|------|------|
| 特征尺度差异大 | 梯度下降收敛慢 | 先标准化（StandardScaler） |
| 特征强共线性 | 系数不稳定、解释失真 | 删除相关特征或加 L2 正则 |
| 类别严重不平衡 | 偏向多数类 | `class_weight='balanced'` 或过采样 |
| 非线性可分 | 线性决策面欠拟合 | 换核方法或集成模型（本章 §5/§6） |
| 过拟合（特征多） | 训练好测试差 | 加 L1/L2 正则、特征选择 |
| 系数解释 | 系数符号/大小反映特征对对数几率的影响 | 输出时同时给系数表 |

#### 1.3 适用范围

| 题型类型 | 典型问题 | 特征 |
|---------|---------|------|
| 二分类 | 信用违约、疾病患病、点击转化 | 类别标签 |
| 多分类 | 品种识别、等级评定 | 多类别 |
| 概率输出 | 风险评分、置信度排序 | 需要 P(y=1\|x) |
| 可解释分类 | 需要系数解读 | 特征影响明确 |

### 可视化图表类型

- **决策边界图**：二维特征下的分类边界
- **ROC 曲线**：不同阈值下的 TPR/FPR
- **系数图**：各特征系数（含显著性）
- **概率分布图**：正负类的预测概率分布
- **校准曲线**：预测概率 vs 实际频率

### 关键文献

| 论文名称 | 作者 | 年份 | 来源 |
|---------|------|------|------|
| Applied Logistic Regression | Hosmer, Lemeshow & Sturdivant | 2013 | Wiley |
| The Elements of Statistical Learning | Hastie, Tibshirani & Friedman | 2009 | Springer |

### 代码实现要点

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, roc_curve, classification_report

def logistic_classification(X_train, y_train, X_test, y_test,
                            C=1.0, penalty='l2', random_state=42):
    """
    逻辑回归分类
    :param X_train: 训练特征
    :param y_train: 训练标签
    :param X_test: 测试特征
    :param y_test: 测试标签
    :param C: 正则化强度（越小正则越强）
    :param penalty: 正则类型 'l1'/'l2'
    :return: 模型, 预测标签, 预测概率, 准确率, AUC
    """
    # 逻辑回归对特征尺度敏感，必须标准化
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = LogisticRegression(C=C, penalty=penalty, solver='liblinear',
                               random_state=random_state, max_iter=1000)
    model.fit(X_train_s, y_train)

    y_pred = model.predict(X_test_s)
    y_proba = model.predict_proba(X_test_s)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print("系数（标准化后，含义=特征对对数几率的影响）:")
    print(f"  截距 b = {model.intercept_[0]:.4f}")
    print("  w =", np.round(model.coef_[0], 4))

    return model, y_pred, y_proba, acc, auc

def plot_roc_lr(y_test, y_proba):
    """绘制逻辑回归 ROC 曲线"""
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    auc = roc_auc_score(y_test, y_proba)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, 'b-', label=f'Logistic Regression (AUC = {auc:.3f})')
    plt.plot([0, 1], [0, 1], 'r--', label='Random')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve - Logistic Regression')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()

# 端到端示例（可直接运行）
if __name__ == '__main__':
    data = load_breast_cancer()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.3, random_state=42)
    model, y_pred, y_proba, acc, auc = logistic_classification(
        X_train, y_train, X_test, y_test)
    print(f"准确率: {acc:.4f}, AUC: {auc:.4f}")
    print(classification_report(y_test, y_pred))
    plot_roc_lr(y_test, y_proba)
```

---

## 2. 决策树 (Decision Tree)

### 算法介绍

决策树是一种**可解释性最强**的分类/回归模型，通过递归特征划分把样本空间分割为若干区域，每个叶节点给出类别（分类）或均值（回归）。竞赛中既单独使用，也作为随机森林/AdaBoost 的基学习器。

#### 2.1 基本原理

**递归划分**：从根节点开始，每个节点选择一个特征和分割阈值，把样本分为左右子树，直到满足停止条件（纯度高、深度达限、样本数过少）。

**分裂准则——信息熵**：
$$
H(D) = -\sum_{k=1}^{K} p_k \log_2 p_k
$$

**信息增益**：
$$
Gain(D, A) = H(D) - \sum_{v=1}^{V} \frac{|D_v|}{|D|} H(D_v)
$$

**分裂准则——基尼不纯度**（CART，sklearn 默认）：
$$
Gini(D) = 1 - \sum_{k=1}^{K} p_k^2
$$

节点分裂时选择使基尼不纯度下降最大的（特征, 阈值）组合。

**剪枝**：
- **预剪枝**：在建树时限制 `max_depth`、`min_samples_split`、`min_samples_leaf` 等，防止过拟合
- **后剪枝**：树建好后自底向上删除对验证集提升不大的子树

#### 2.2 使用条件与常见坑

| 条件/坑 | 说明 | 应对 |
|---------|------|------|
| 极易过拟合 | 不剪枝可 100% 拟合训练集 | 限制 max_depth（如 3-8）、min_samples_leaf |
| 对特征尺度不敏感 | 按阈值分裂，无需标准化 | 天然优势，但数值型特征离散化效果更好 |
| 连续特征多 | 分裂点搜索耗时长 | 特征分箱（K-Bins）或限制 max_features |
| 类别不平衡 | 偏向多数类 | 设 class_weight 或调整分裂阈值 |
| 高方差 | 训练集微扰导致树结构剧变 | 用随机森林（本章 §6）集成降方差 |
| 特征重要性 | `feature_importances_` 反映对纯度的贡献 | 用于特征选择，但需注意偏差（偏向高基数特征） |

#### 2.3 适用范围

| 题型类型 | 典型问题 | 特征 |
|---------|---------|------|
| 分类预测 | 等级判定、风险分层 | 类别标签 |
| 规则提取 | 需要可解释决策规则 | 业务规则 |
| 特征选择 | 关键特征识别 | 高维数据 |
| 基学习器 | 随机森林/AdaBoost 的基模型 | 集成学习 |

### 可视化图表类型

- **树结构图**：`sklearn.tree.plot_tree` 可视化整棵树
- **特征重要性图**：各特征基尼重要性排序
- **决策边界图**：二维特征分类边界（呈阶梯状）
- **剪枝对比图**：不同 max_depth 的精度对比

### 关键文献

| 论文名称 | 作者 | 年份 | 来源 |
|---------|------|------|------|
| Classification and Regression Trees | Breiman et al. | 1984 | Wadsworth |
| Induction of Decision Trees | Quinlan | 1986 | Machine Learning |

### 代码实现要点

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score

def decision_tree_classification(X_train, y_train, X_test, y_test,
                                 max_depth=5, min_samples_leaf=2, random_state=42):
    """
    决策树分类
    :param X_train: 训练特征
    :param y_train: 训练标签
    :param X_test: 测试特征
    :param y_test: 测试标签
    :param max_depth: 最大深度（剪枝，防过拟合）
    :param min_samples_leaf: 叶节点最少样本数
    :return: 模型, 预测结果, 准确率, 交叉验证分数
    """
    model = DecisionTreeClassifier(max_depth=max_depth,
                                   min_samples_leaf=min_samples_leaf,
                                   random_state=random_state)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    # 交叉验证评估泛化能力
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)

    return model, y_pred, acc, cv_scores

def plot_tree_structure(model, feature_names, class_names):
    """可视化决策树结构"""
    plt.figure(figsize=(20, 10))
    plot_tree(model, feature_names=feature_names, class_names=class_names,
              filled=True, rounded=True, fontsize=10)
    plt.title('Decision Tree Structure')
    plt.show()

def tune_max_depth(X_train, y_train, X_test, y_test, max_depths=range(1, 11)):
    """调 max_depth：找到验证集最优深度"""
    train_accs, test_accs = [], []
    for d in max_depths:
        model = DecisionTreeClassifier(max_depth=d, random_state=42)
        model.fit(X_train, y_train)
        train_accs.append(accuracy_score(y_train, model.predict(X_train)))
        test_accs.append(accuracy_score(y_test, model.predict(X_test)))

    plt.figure(figsize=(8, 6))
    plt.plot(list(max_depths), train_accs, 'o-', label='Train Accuracy')
    plt.plot(list(max_depths), test_accs, 's-', label='Test Accuracy')
    plt.xlabel('Max Depth')
    plt.ylabel('Accuracy')
    plt.title('Decision Tree: Accuracy vs Max Depth')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()
    return test_accs

# 端到端示例（可直接运行）
if __name__ == '__main__':
    data = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.3, random_state=42)
    model, y_pred, acc, cv = decision_tree_classification(
        X_train, y_train, X_test, y_test, max_depth=4)
    print(f"准确率: {acc:.4f}, 5折CV均值: {cv.mean():.4f}")
    plot_tree_structure(model, data.feature_names, data.target_names)
```

---

## 3. K近邻 (K-Nearest Neighbors, KNN)

### 算法介绍

KNN 是一种**基于实例**的惰性学习算法：不做显式训练，预测时直接找与待测样本最近的 K 个训练样本，按多数投票（分类）或均值（回归）给出结果。原理直观、实现简单，适合中小规模数据。

#### 3.1 基本原理

**距离度量**（闵可夫斯基距离，$p=2$ 时是欧氏距离）：
$$
d(x, y) = \left( \sum_{j=1}^{m} |x_j - y_j|^p \right)^{1/p}
$$

**分类决策**（多数投票）：
$$
\hat{y}(x) = \arg\max_{c} \sum_{i \in N_K(x)} \mathbb{I}(y_i = c)
$$

其中 $N_K(x)$ 是 $x$ 的 K 个最近邻集合。

**回归决策**（均值）：
$$
\hat{y}(x) = \frac{1}{K} \sum_{i \in N_K(x)} y_i
$$

**加权投票**（可选）：距离越近权重越大，$w_i = 1/d(x, x_i)$。

#### 3.2 使用条件与常见坑

| 条件/坑 | 说明 | 应对 |
|---------|------|------|
| **必须特征缩放** | 量纲差异大时距离被大尺度特征主导 | 用 StandardScaler/MinMaxScaler 先归一化 |
| K 值选择 | K 太小过拟合，太大欠拟合 | 交叉验证选 K（常用 3-15 的奇数） |
| 维度灾难 | 高维下距离区分度急剧下降 | 先用 PCA（05 §4）降维或换模型 |
| 预测耗时 | 无训练但有预测 O(n)，样本大时慢 | 大数据集换决策树/逻辑回归 |
| 类别不平衡 | 多数类邻居占优 | 加权投票或过采样 |
| 特征冗余 | 无关特征污染距离 | 特征选择后再用 |

#### 3.3 适用范围

| 题型类型 | 典型问题 | 特征 |
|---------|---------|------|
| 分类预测 | 品种识别、相似匹配 | 中小规模 |
| 回归预测 | 相似样本估值 | 连续目标 |
| 异常检测 | 距离异常点 | 无标签可用 |
| 缺失值填充 | 用近邻均值填充 | 05 §1.1 |

### 可视化图表类型

- **决策边界图**：KNN 分类边界（非线性的锯齿边界）
- **K 值调参曲线**：不同 K 的精度变化
- **距离分布图**：近邻距离直方图
- **最近邻连线图**：二维下样本与近邻连线

### 关键文献

| 论文名称 | 作者 | 年份 | 来源 |
|---------|------|------|------|
| Nearest neighbor pattern classification | Cover & Hart | 1967 | IEEE Trans. IT |
| The Elements of Statistical Learning | Hastie, Tibshirani & Friedman | 2009 | Springer |

### 代码实现要点

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score

def knn_classification(X_train, y_train, X_test, y_test, k=5, weights='distance'):
    """
    KNN 分类
    :param X_train: 训练特征
    :param y_train: 训练标签
    :param X_test: 测试特征
    :param y_test: 测试标签
    :param k: 近邻数
    :param weights: 'uniform' 等权 / 'distance' 距离加权
    :return: 模型, 预测结果, 准确率
    """
    # 关键：KNN 对特征尺度极度敏感，必须先标准化
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = KNeighborsClassifier(n_neighbors=k, weights=weights, p=2)
    model.fit(X_train_s, y_train)

    y_pred = model.predict(X_test_s)
    acc = accuracy_score(y_test, y_pred)

    return model, y_pred, acc, scaler

def tune_k(X_train, y_train, X_test, y_test, k_range=range(1, 21)):
    """调 K：交叉验证找最优近邻数（奇数优先）"""
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    cv_means, test_accs = [], []
    for k in k_range:
        model = KNeighborsClassifier(n_neighbors=k, weights='distance')
        cv = cross_val_score(model, X_train_s, y_train, cv=5).mean()
        model.fit(X_train_s, y_train)
        test_accs.append(accuracy_score(y_test, model.predict(X_test_s)))
        cv_means.append(cv)

    best_k = k_range[int(np.argmax(cv_means))]

    plt.figure(figsize=(8, 6))
    plt.plot(list(k_range), cv_means, 'o-', label='CV Accuracy')
    plt.plot(list(k_range), test_accs, 's-', label='Test Accuracy')
    plt.axvline(best_k, color='r', linestyle='--', label=f'Best K={best_k}')
    plt.xlabel('K')
    plt.ylabel('Accuracy')
    plt.title('KNN: Accuracy vs K')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()
    return best_k

# 端到端示例（可直接运行）
if __name__ == '__main__':
    data = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.3, random_state=42)
    model, y_pred, acc, scaler = knn_classification(X_train, y_train, X_test, y_test, k=5)
    print(f"K=5 准确率: {acc:.4f}")
    best_k = tune_k(X_train, y_train, X_test, y_test)
    print(f"交叉验证最优 K = {best_k}")
```

---

## 4. 朴素贝叶斯 (Naive Bayes)

### 算法介绍

朴素贝叶斯基于**贝叶斯定理**和**特征条件独立假设**构建分类器。尽管"朴素"假设在现实中常不成立，它在文本分类、小样本场景下仍表现出色，训练只需统计先验和条件概率，速度极快。

#### 4.1 基本原理

**贝叶斯定理**：
$$
P(y|x) = \frac{P(x|y) P(y)}{P(x)} = \frac{P(x_1, x_2, \ldots, x_m | y) P(y)}{P(x)}
$$

**朴素假设**（特征条件独立）：
$$
P(x|y) = \prod_{j=1}^{m} P(x_j | y)
$$

**分类决策**（最大后验，分母 P(x) 与类别无关可省略）：
$$
\hat{y} = \arg\max_{y} P(y) \prod_{j=1}^{m} P(x_j | y)
$$

**三种变体**（区别在 P(x_j|y) 的建模方式）：

| 变体 | 适用特征 | 条件分布 |
|------|---------|---------|
| 高斯朴素贝叶斯 GaussianNB | 连续数值特征 | $P(x_j\|y) = \mathcal{N}(x_j; \mu_{jy}, \sigma_{jy}^2)$ |
| 多项式朴素贝叶斯 MultinomialNB | 非负计数特征（词频） | 多项式分布 |
| 伯努利朴素贝叶斯 BernoulliNB | 二值特征（出现/不出现） | 伯努利分布 |

**平滑**：为避免某特征在训练集未出现导致概率为 0，加拉普拉斯平滑 $P(x_j|y) = \frac{N_{jy} + \alpha}{N_y + \alpha \cdot V}$。

#### 4.2 使用条件与常见坑

| 条件/坑 | 说明 | 应对 |
|---------|------|------|
| 特征独立假设 | 强相关特征会低估真实概率 | 相关特征严重时换逻辑回归/决策树 |
| 连续特征分布 | 高斯 NB 假设正态，偏态分布效果差 | 先变换或分箱成离散特征用多项式 NB |
| 特征零频率 | 测试出现训练未见的特征值 | 默认已加拉普拉斯平滑，可调 alpha |
| 小样本优势 | 参数少、方差小，小数据表现好 | 是优点，竞赛小样本赛题可用 |
| 文本/计数任务 | 词频特征下是最强基线之一 | MultinomialNB 配 TF-IDF |

#### 4.3 适用范围

| 题型类型 | 典型问题 | 特征 |
|---------|---------|------|
| 文本分类 | 垃圾邮件、情感分析 | 词频/词向量 |
| 疾病诊断 | 症状推断疾病 | 特征条件独立近似成立 |
| 实时分类 | 大规模流式预测 | 训练/预测极快 |
| 小样本分类 | 竞赛少量数据 | 参数少方差小 |

### 可视化图表类型

- **特征条件分布图**：各类别下各特征的分布
- **决策边界图**：二维特征分类边界
- **概率输出图**：各类预测概率
- **性能对比图**：不同 NB 变体对比

### 关键文献

| 论文名称 | 作者 | 年份 | 来源 |
|---------|------|------|------|
| An empirical study of the naive Bayes classifier | Rish | 2001 | IJCAI Workshop |
| The Elements of Statistical Learning | Hastie, Tibshirani & Friedman | 2009 | Springer |

### 代码实现要点

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

def gaussian_nb_classification(X_train, y_train, X_test, y_test, var_smoothing=1e-9):
    """
    高斯朴素贝叶斯分类（连续特征）
    :param X_train: 训练特征
    :param y_train: 训练标签
    :param X_test: 测试特征
    :param y_test: 测试标签
    :param var_smoothing: 方差平滑项，避免方差为 0 导致概率为 0
    :return: 模型, 预测结果, 准确率, 预测概率
    """
    model = GaussianNB(var_smoothing=var_smoothing)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    acc = accuracy_score(y_test, y_pred)

    print("各类别先验 P(y):", np.round(model.class_prior_, 4))
    print("各特征均值 mu（shape=类别数×特征数）:\n", np.round(model.theta_, 4))

    return model, y_pred, y_proba, acc

def naive_bayes_variant_comparison(X_train, y_train, X_test, y_test):
    """
    三种 NB 变体对比（需特征形式匹配）：
    - GaussianNB: 连续数值
    - MultinomialNB: 非负计数
    - BernoulliNB: 二值
    """
    results = {}
    for name, model in [
        ('GaussianNB', GaussianNB()),
        ('MultinomialNB', MultinomialNB()),
        ('BernoulliNB', BernoulliNB()),
    ]:
        model.fit(X_train, y_train)
        results[name] = accuracy_score(y_test, model.predict(X_test))
    return results

# 端到端示例（可直接运行）
if __name__ == '__main__':
    data = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.3, random_state=42)
    model, y_pred, y_proba, acc = gaussian_nb_classification(X_train, y_train, X_test, y_test)
    print(f"高斯朴素贝叶斯准确率: {acc:.4f}")
    print(classification_report(y_test, y_pred))
```

---

## 5. 支持向量机分类 (Support Vector Machine for Classification, SVC)

### 算法介绍

SVM 通过寻找**最大间隔**分类超平面提升泛化能力，配合**核技巧**可处理非线性分类。对中小规模数据表现优异，是竞赛中常用的强分类器。**注意**：`02-预测类算法说明.md` §5 是 SVR（回归），本章是 SVC（分类），两者数学同源但目标不同。

#### 5.1 基本原理

**线性可分硬间隔**（最大化 $\frac{2}{\|w\|}$ 即最小化 $\|w\|$）：
$$
\min_{w,b} \frac{1}{2}\|w\|^2, \quad \text{s.t.} \quad y_i(w^T x_i + b) \geq 1, \; i=1,\ldots,n
$$

**软间隔**（引入松弛变量 $\xi_i$，容忍少量误分，$C$ 控制惩罚力度）：
$$
\min_{w,b,\xi} \frac{1}{2}\|w\|^2 + C\sum_{i=1}^{n} \xi_i, \quad \text{s.t.} \quad y_i(w^T x_i + b) \geq 1 - \xi_i, \; \xi_i \geq 0
$$

**对偶问题与核技巧**：
$$
\max_{\alpha} \sum_{i=1}^{n} \alpha_i - \frac{1}{2} \sum_{i,j} \alpha_i \alpha_j y_i y_j K(x_i, x_j)
$$

约束 $\sum_{i} \alpha_i y_i = 0, \; 0 \leq \alpha_i \leq C$，其中核函数 $K$ 把样本隐式映射到高维空间。

**常用核函数**：
- 线性核：$K(x,x') = x^T x'$
- 多项式核：$K(x,x') = (x^T x' + c)^d$
- **RBF 核**（默认，最常用）：$K(x,x') = \exp(-\gamma \|x-x'\|^2)$

**支持向量**：满足 $0 < \alpha_i \leq C$ 的样本，决定决策边界，其余样本不影响。

#### 5.2 使用条件与常见坑

| 条件/坑 | 说明 | 应对 |
|---------|------|------|
| **必须特征标准化** | 间隔依赖尺度，不标准化 RBF 核失效 | 必须先 StandardScaler |
| C 与 γ 高度耦合 | 参数敏感，直接决定边界复杂度 | 网格搜索 `GridSearchCV` 联合调 C、γ |
| 对噪声敏感 | 硬间隔会被噪声样本带偏 | 减小 C（允许更多容错） |
| 大数据集慢 | 非线性核求解是 O(n²)~O(n³) | 大数据换线性核/逻辑回归/随机森林 |
| 多分类 | 默认 OvO 二分类组合 | 调 `decision_function_shape`，或显式 OvR |
| 概率输出 | `predict_proba` 需 Platt 校准，较慢 | 需要概率时可用逻辑回归替代 |

#### 5.3 适用范围

| 题型类型 | 典型问题 | 特征 |
|---------|---------|------|
| 中小规模分类 | 图像识别、文本分类 | n ≤ 10⁴~10⁵ |
| 高维小样本 | 基因表达、稀疏特征 | 特征数大样本数小 |
| 非线性边界 | 复杂决策面 | RBF 核 |
| 异常检测 | 单类 SVM | 无监督变体 |

### 可视化图表类型

- **决策边界图**：SVM 分类边界 + 支持向量高亮
- **核函数对比图**：不同核的边界效果
- **参数敏感性图**：C、γ 对精度的热力图
- **间隔可视化**：最大间隔超平面（二维）

### 关键文献

| 论文名称 | 作者 | 年份 | 来源 |
|---------|------|------|------|
| Support Vector Networks | Cortes & Vapnik | 1995 | Machine Learning |
| A Tutorial on Support Vector Machines for Pattern Recognition | Burges | 1998 | Data Mining and Knowledge Discovery |

### 代码实现要点

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report

def svc_classification(X_train, y_train, X_test, y_test,
                       C=1.0, gamma='scale', kernel='rbf', random_state=42):
    """
    SVM 分类
    :param X_train: 训练特征
    :param y_train: 训练标签
    :param X_test: 测试特征
    :param y_test: 测试标签
    :param C: 正则化（容错）参数
    :param gamma: RBF 核带宽（'scale'/'auto' 或数值）
    :param kernel: 核函数
    :return: 模型, 预测结果, 准确率, 支持向量数
    """
    # 关键：SVM 对特征尺度极度敏感，必须先标准化
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = SVC(C=C, gamma=gamma, kernel=kernel, random_state=random_state)
    model.fit(X_train_s, y_train)

    y_pred = model.predict(X_test_s)
    acc = accuracy_score(y_test, y_pred)

    return model, y_pred, acc, len(model.support_)

def svc_grid_search(X_train, y_train, X_test, y_test):
    """C、γ 联合网格搜索（SVM 参数敏感性高，务必调参）"""
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    param_grid = {
        'C': [0.1, 1, 10, 100],
        'gamma': ['scale', 'auto', 0.01, 0.1, 1],
        'kernel': ['rbf', 'linear'],
    }
    model = SVC()
    grid = GridSearchCV(model, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
    grid.fit(X_train_s, y_train)

    print(f"最优参数: {grid.best_params_}")
    print(f"最优CV准确率: {grid.best_score_:.4f}")

    y_pred = grid.best_estimator_.predict(X_test_s)
    acc = accuracy_score(y_test, y_pred)
    return grid.best_estimator_, y_pred, acc, grid.best_params_

# 端到端示例（可直接运行）
if __name__ == '__main__':
    data = load_breast_cancer()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.3, random_state=42)
    model, y_pred, acc, n_sv = svc_classification(X_train, y_train, X_test, y_test)
    print(f"SVC(RBF) 准确率: {acc:.4f}, 支持向量数: {n_sv}")
    best, y_pred_b, acc_b, params = svc_grid_search(X_train, y_train, X_test, y_test)
    print(f"调参后准确率: {acc_b:.4f}")
```

---

## 6. 随机森林 (Random Forest)

### 算法介绍

随机森林是一种集成学习方法，通过构建多棵决策树并合并它们的预测结果来提高模型的泛化能力和稳定性。

#### 6.1 基本原理

**Bagging（Bootstrap Aggregating）**：
- 有放回抽样生成多个训练集
- 每个训练集训练一个基学习器
- 合并预测结果（投票或平均）

**随机特征选择**：
- 每个节点分裂时，随机选择一部分特征
- 增加树之间的多样性
- 减少方差

#### 6.2 回归随机森林

**预测**：
$$
\hat{y} = \frac{1}{T} \sum_{t=1}^{T} f_t(x)
$$

其中$T$是树的数量，$f_t(x)$是第$t$棵树的预测值。

**OOB误差（Out-of-Bag Error）**：
- 使用未被抽样的样本（袋外数据）验证
- 交叉验证的替代方案

#### 6.3 分类随机森林

**多数投票**：
$$
\hat{y} = \arg\max_{c} \sum_{t=1}^{T} \mathbb{I}(f_t(x) = c)
$$

**概率估计**：
$$
P(c|x) = \frac{1}{T} \sum_{t=1}^{T} \mathbb{I}(f_t(x) = c)
$$

#### 6.4 特征重要性

**Gini重要性**：
$$
GI_j = \frac{1}{T} \sum_{t=1}^{T} \Delta GI_{jt}
$$

其中$\Delta GI_{jt}$是特征$j$在树$t$中带来的Gini不纯度减少量。

**置换重要性**：
- 随机打乱某特征值
- 观察预测误差的变化
- 误差增加越多，特征越重要

#### 6.5 使用条件与常见坑

| 条件/坑 | 说明 | 应对 |
|---------|------|------|
| 大数据集慢 | 树多、特征多时训练慢 | 限制 n_estimators、max_features |
| 类别不平衡 | 偏向多数类 | class_weight='balanced' 或采样 |
| 特征重要性偏差 | 高基数特征被高估 | 用置换重要性 `permutation_importance` 交叉验证 |
| 回归外推差 | 无法外推超出训练范围 | 回归外推时换线性/树外模型 |
| 过拟合 | 树深 + 树多可能过拟合 | 限制 max_depth、min_samples_leaf |

### 适用范围

| 题型类型 | 典型问题 | 特征 |
|---------|---------|------|
| 分类预测 | 客户流失、疾病诊断 | 分类标签 |
| 回归预测 | 房价、销量预测 | 连续目标 |
| 特征选择 | 关键特征识别 | 高维数据 |
| 异常检测 | 欺诈检测 | 不平衡数据 |
| 数据缺失 | 含缺失值数据 | 鲁棒性强 |

### 可视化图表类型

- **特征重要性图**：各特征重要性排序
- **决策树可视化**：单棵树结构
- **OOB误差曲线**：误差随树数变化
- **偏依赖图**：特征对预测的影响
- **类别概率图**：分类概率分布

### 关键文献

| 论文名称 | 作者 | 年份 | 来源 |
|---------|------|------|------|
| Random Forests | Breiman | 2001 | Machine Learning |
| Classification and Regression Trees | Breiman et al. | 1984 | Wadsworth |

### 代码实现要点

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error
import matplotlib.pyplot as plt

def random_forest_classification(X_train, y_train, X_test, y_test,
                                  n_estimators=100, max_depth=None, random_state=42):
    """
    随机森林分类
    :param X_train: 训练特征
    :param y_train: 训练标签
    :param X_test: 测试特征
    :param y_test: 测试标签
    :return: 模型, 预测结果, OOB分数
    """
    rf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        oob_score=True,
        n_jobs=-1
    )

    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    y_proba = rf.predict_proba(X_test)

    accuracy = accuracy_score(y_test, y_pred)

    return rf, y_pred, y_proba, accuracy, rf.oob_score_

def random_forest_regression(X_train, y_train, X_test, y_test,
                              n_estimators=100, max_depth=None, random_state=42):
    """
    随机森林回归
    :param X_train: 训练特征
    :param y_train: 训练目标
    :param X_test: 测试特征
    :param y_test: 测试目标
    :return: 模型, 预测结果, MSE, OOB分数
    """
    rf = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        oob_score=True,
        n_jobs=-1
    )

    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)

    return rf, y_pred, mse, rf.oob_score_

def plot_feature_importance(rf_model, feature_names, top_n=20):
    """
    绘制特征重要性
    :param rf_model: 随机森林模型
    :param feature_names: 特征名称列表
    :param top_n: 显示前N个特征
    """
    importances = rf_model.feature_importances_
    indices = np.argsort(importances)[::-1][:top_n]

    plt.figure(figsize=(10, 6))
    plt.bar(range(len(indices)), importances[indices])
    plt.xticks(range(len(indices)), [feature_names[i] for i in indices], rotation=90)
    plt.xlabel('Feature')
    plt.ylabel('Importance')
    plt.title('Feature Importance (Random Forest)')
    plt.tight_layout()
    plt.show()

def plot_oob_error(X, y, max_estimators=200):
    """
    绘制OOB误差随树数变化
    :param X: 特征矩阵
    :param y: 目标变量
    :param max_estimators: 最大树数
    """
    oob_errors = []

    for n in range(1, max_estimators + 1, 5):
        if len(np.unique(y)) <= 10:  # 分类
            rf = RandomForestClassifier(n_estimators=n, oob_score=True,
                                        random_state=42, n_jobs=-1)
            rf.fit(X, y)
            oob_errors.append(1 - rf.oob_score_)
        else:  # 回归
            rf = RandomForestRegressor(n_estimators=n, oob_score=True,
                                       random_state=42, n_jobs=-1)
            rf.fit(X, y)
            oob_errors.append(rf.oob_score_)

    plt.figure(figsize=(10, 6))
    plt.plot(range(1, max_estimators + 1, 5), oob_errors, 'o-')
    plt.xlabel('Number of Trees')
    plt.ylabel('OOB Error')
    plt.title('Random Forest: OOB Error vs Number of Trees')
    plt.show()

def plot_partial_dependence(rf_model, X, feature_names, feature_idx):
    """
    绘制偏依赖图
    :param rf_model: 随机森林模型
    :param X: 特征矩阵
    :param feature_names: 特征名称
    :param feature_idx: 特征索引
    """
    from sklearn.inspection import PartialDependenceDisplay

    PartialDependenceDisplay.from_estimator(rf_model, X, [feature_idx],
                                              feature_names=feature_names,
                                              kind='average')
    plt.show()
```

---

## 7. AdaBoost (Adaptive Boosting)

### 算法介绍

AdaBoost是一种自适应提升算法，通过迭代训练弱分类器并调整样本权重来构建强分类器。

#### 7.1 基本原理

**核心思想**：
- 训练一系列弱分类器
- 每轮关注之前分类错误的样本
- 组合多个弱分类器形成强分类器

**算法流程**：

1. 初始化样本权重：$w_i^{(1)} = 1/n$，$i = 1, 2, \ldots, n$

2. 对于$t = 1, 2, \ldots, T$：
   - 使用权重$w^{(t)}$训练弱分类器$h_t(x)$
   - 计算分类错误率：$\epsilon_t = \sum_{i=1}^{n} w_i^{(t)} \mathbb{I}(y_i \neq h_t(x_i))$
   - 计算分类器权重：$\alpha_t = \frac{1}{2} \ln\left(\frac{1-\epsilon_t}{\epsilon_t}\right)$
   - 更新样本权重：
     $$
     w_i^{(t+1)} = \frac{w_i^{(t)} \exp(-\alpha_t y_i h_t(x_i))}{\sum_{j=1}^{n} w_j^{(t)} \exp(-\alpha_t y_j h_t(x_j))}
     $$

3. 最终分类器：
   $$
   H(x) = \text{sign}\left( \sum_{t=1}^{T} \alpha_t h_t(x) \right)
   $$

#### 7.2 AdaBoost变体

**AdaBoost.M1**：二分类版本

**AdaBoost.M2**：多分类版本

**AdaBoost.R2**：回归版本

#### 7.3 梯度提升

**梯度提升机（GBM）**：
- 使用梯度下降方向训练新分类器
- 拟合负梯度（残差）
- 更灵活，可使用任意损失函数

**与AdaBoost关系**：
- AdaBoost是指数损失下的梯度提升
- GBM推广到任意可微损失函数

#### 7.4 使用条件与常见坑

| 条件/坑 | 说明 | 应对 |
|---------|------|------|
| 对噪声/异常敏感 | 异常样本权重被放大 | 数据清洗后再用；噪声多时换随机森林 |
| 弱分类器选择 | 默认决策树桩（depth=1） | 可试 depth=2-3 平衡偏差/方差 |
| 类别不平衡 | 提升法对不平衡敏感 | 用 `sample_weight` 或换 BalancedRandomForest |
| 性能提升有限 | 数据已较易分类时收益小 | 对比随机森林/XGBoost（02 §9）再选 |
| 与 XGBoost 关系 | AdaBoost 是梯度提升的特例 | 追求更强效果用 XGBoost，见 02 §9 |

### 适用范围

| 题型类型 | 典型问题 | 特征 |
|---------|---------|------|
| 二分类 | 欺诈检测、垃圾邮件 | 标签不平衡 |
| 多分类 | 图像分类、文本分类 | 多类别 |
| 回归 | 价格预测、需求预测 | 连续目标 |
| 特征工程 | 特征选择 | 重要特征 |
| 集成学习 | 模型融合 | 提升性能 |

### 可视化图表类型

- **错误率曲线**：训练/测试错误率随轮数变化
- **分类器权重图**：各弱分类器权重
- **决策边界图**：分类边界可视化
- **特征重要性图**：特征重要性排序
- **残差图**：残差随轮数变化（回归）

### 关键文献

| 论文名称 | 作者 | 年份 | 来源 |
|---------|------|------|------|
| A decision-theoretic generalization of on-line learning | Freund & Schapire | 1995 | Journal of Computer and System Sciences |
| A short introduction to boosting | Schapire & Freund | 2012 | Journal of Japanese Society for Artificial Intelligence |
| Greedy Function Approximation: A Gradient Boosting Machine | Friedman | 2001 | Annals of Statistics |

### 代码实现要点

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import AdaBoostClassifier, AdaBoostRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.metrics import accuracy_score, mean_squared_error

def adaboost_classification(X_train, y_train, X_test, y_test,
                             n_estimators=50, learning_rate=1.0, random_state=42):
    """
    AdaBoost分类
    :param X_train: 训练特征
    :param y_train: 训练标签
    :param X_test: 测试特征
    :param y_test: 测试标签
    :param n_estimators: 弱分类器数量
    :param learning_rate: 学习率
    :return: 模型, 预测结果, 准确率, 错误率历史
    """
    # 基分类器：决策树桩（深度为1）
    base_clf = DecisionTreeClassifier(max_depth=1)

    ada = AdaBoostClassifier(
        estimator=base_clf,
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        random_state=random_state
    )

    ada.fit(X_train, y_train)
    y_pred = ada.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # 计算训练过程中的错误率
    train_errors = []
    for y_pred_train in ada.staged_predict(X_train):
        err = 1 - accuracy_score(y_train, y_pred_train)
        train_errors.append(err)

    test_errors = []
    for y_pred_test in ada.staged_predict(X_test):
        err = 1 - accuracy_score(y_test, y_pred_test)
        test_errors.append(err)

    return ada, y_pred, accuracy, train_errors, test_errors

def adaboost_regression(X_train, y_train, X_test, y_test,
                         n_estimators=50, learning_rate=1.0, loss='linear', random_state=42):
    """
    AdaBoost回归
    :param X_train: 训练特征
    :param y_train: 训练目标
    :param X_test: 测试特征
    :param y_test: 测试目标
    :param loss: 损失函数 ('linear', 'square', 'exponential')
    :return: 模型, 预测结果, MSE
    """
    base_reg = DecisionTreeRegressor(max_depth=3)

    ada = AdaBoostRegressor(
        estimator=base_reg,
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        loss=loss,
        random_state=random_state
    )

    ada.fit(X_train, y_train)
    y_pred = ada.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)

    # 计算训练过程中的MSE
    train_mse = []
    for y_pred_train in ada.staged_predict(X_train):
        mse_val = mean_squared_error(y_train, y_pred_train)
        train_mse.append(mse_val)

    test_mse = []
    for y_pred_test in ada.staged_predict(X_test):
        mse_val = mean_squared_error(y_test, y_pred_test)
        test_mse.append(mse_val)

    return ada, y_pred, mse, train_mse, test_mse

def plot_adaboost_errors(train_errors, test_errors, title="AdaBoost Error Rate"):
    """
    绘制AdaBoost错误率曲线
    :param train_errors: 训练错误率列表
    :param test_errors: 测试错误率列表
    :param title: 图标题
    """
    plt.figure(figsize=(10, 6))
    plt.plot(train_errors, 'o-', label='Train Error')
    plt.plot(test_errors, 's-', label='Test Error')
    plt.xlabel('Number of Estimators')
    plt.ylabel('Error Rate')
    plt.title(title)
    plt.legend()
    plt.show()

def plot_feature_importance_adaboost(ada_model, feature_names, top_n=20):
    """
    绘制特征重要性（AdaBoost）
    :param ada_model: AdaBoost模型
    :param feature_names: 特征名称
    :param top_n: 显示前N个特征
    """
    importances = ada_model.feature_importances_
    indices = np.argsort(importances)[::-1][:top_n]

    plt.figure(figsize=(10, 6))
    plt.bar(range(len(indices)), importances[indices])
    plt.xticks(range(len(indices)), [feature_names[i] for i in indices], rotation=90)
    plt.xlabel('Feature')
    plt.ylabel('Importance')
    plt.title('Feature Importance (AdaBoost)')
    plt.tight_layout()
    plt.show()

def plot_decision_boundary(model, X, y, title="Decision Boundary"):
    """
    绘制决策边界（适用于2D特征）
    :param model: 训练好的模型
    :param X: 特征矩阵
    :param y: 标签
    :param title: 图标题
    """
    if X.shape[1] != 2:
        print("Decision boundary plot only works for 2D features")
        return

    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1),
                         np.arange(y_min, y_max, 0.1))

    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    plt.figure(figsize=(10, 6))
    plt.contourf(xx, yy, Z, alpha=0.3, cmap=plt.cm.Paired)
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.Paired, edgecolors='k')
    plt.xlabel('Feature 1')
    plt.ylabel('Feature 2')
    plt.title(title)
    plt.tight_layout()
    plt.show()
```

---

## 8. 孤立森林 (Isolation Forest)

### 算法介绍

孤立森林是一种异常检测算法，通过随机分割特征空间来隔离数据点，异常点更容易被隔离（需要更少的分割步骤）。

#### 8.1 基本原理

**核心思想**：
- 异常点是少数且不同的
- 异常点更容易被孤立
- 使用路径长度衡量异常程度

**孤立树（iTree）构建**：

1. 随机选择特征和分割值
2. 递归分割数据空间
3. 直到：所有数据点被孤立 或 达到最大深度

**路径长度**：
$$
h(x) = \sum_{i=1}^{\text{path}} \Delta i + C(\psi)
$$

其中$\Delta i$是节点到子节点的路径长度，$C(\psi)$是调整项。

#### 8.2 异常得分

**归一化路径长度**：
$$
H(x) = h(x) / c(\psi)
$$

其中$c(\psi) = 2H(\psi - 1) - (2(\psi - 1)/\psi)$是调整路径长度，$\psi$是样本数。

**异常得分**：
$$
s(x, \psi) = 2^{-\frac{E[H(x)]}{c(\psi)}}
$$

**得分解释**：
- $s \approx 1$：异常点
- $s < 0.5$：正常点
- $s \approx 0.5$：无异常

#### 8.3 算法特点

**优点**：
- 无需假设数据分布
- 线性时间复杂度
- 内存效率高
- 可处理高维数据

**参数**：
- `n_estimators`：树的数量
- `max_samples`：每棵树的样本数
- `contamination`：异常比例

#### 8.4 使用条件与常见坑

| 条件/坑 | 说明 | 应对 |
|---------|------|------|
| contamination 需先验 | 异常比例假设影响阈值 | 无先验时用 0.1 起调，结合得分分布定阈值 |
| 高维效果下降 | 维度极高时路径长度区分度降低 | 先 PCA（05 §4）降维 |
| 不适合密集簇数据 | 正常点也聚集时误报多 | 正常点聚集时考虑 LOF/密度方法 |
| 异常标签语义 | predict 返回 1/-1，score_samples 越大越异常 | 转 0/1 统一口径 |

### 适用范围

| 题型类型 | 典型问题 | 特征 |
|---------|---------|------|
| 欺诈检测 | 信用卡欺诈 | 极度不平衡 |
| 网络入侵 | 异常流量 | 异常模式 |
| 设备故障 | 设备异常检测 | 传感器数据 |
| 数据清洗 | 异常值识别 | 数据质量 |
| 医疗诊断 | 罕见病识别 | 罕见模式 |

### 可视化图表类型

- **异常得分图**：各样本异常得分
- **异常散点图**：异常点在特征空间的分布
- **路径长度分布**：路径长度直方图
- **ROC曲线**：检测性能评估
- **2D投影图**：二维特征空间的异常点

### 关键文献

| 论文名称 | 作者 | 年份 | 来源 |
|---------|------|------|------|
| Isolation Forest | Liu, Ting, & Zhou | 2008 | ICDM |
| Isolation-based Anomaly Detection | Liu, Ting, & Zhou | 2012 | ACM TKDD |

### 代码实现要点

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, roc_auc_score, roc_curve

def isolation_forest_anomaly_detection(X, contamination=0.1, random_state=42):
    """
    孤立森林异常检测
    :param X: 特征矩阵
    :param contamination: 异常比例
    :return: 模型, 异常标签, 异常得分
    """
    iso_forest = IsolationForest(
        n_estimators=100,
        max_samples='auto',
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1
    )

    iso_forest.fit(X)

    # 预测：-1表示异常，1表示正常
    labels = iso_forest.predict(X)

    # 计算异常得分（越大越异常）
    scores = iso_forest.score_samples(X)
    anomaly_scores = -scores

    return iso_forest, labels, anomaly_scores

def plot_anomaly_scores(X, anomaly_scores, labels, feature_names=None):
    """
    绘制异常得分可视化
    :param X: 特征矩阵
    :param anomaly_scores: 异常得分
    :param labels: 异常标签
    :param feature_names: 特征名称
    """
    if X.shape[1] < 2:
        print("Need at least 2 features for visualization")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 散点图（使用前两个特征）
    normal_mask = labels == 1
    anomaly_mask = labels == -1

    axes[0].scatter(X[normal_mask, 0], X[normal_mask, 1],
                   c='blue', label='Normal', alpha=0.5)
    axes[0].scatter(X[anomaly_mask, 0], X[anomaly_mask, 1],
                   c='red', label='Anomaly', alpha=0.8)
    axes[0].set_xlabel(feature_names[0] if feature_names else 'Feature 1')
    axes[0].set_ylabel(feature_names[1] if feature_names else 'Feature 2')
    axes[0].set_title('Anomaly Detection Results')
    axes[0].legend()

    # 异常得分分布
    axes[1].hist(anomaly_scores[normal_mask], bins=50, alpha=0.5,
                label='Normal', color='blue')
    axes[1].hist(anomaly_scores[anomaly_mask], bins=50, alpha=0.5,
                label='Anomaly', color='red')
    axes[1].set_xlabel('Anomaly Score')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title('Anomaly Score Distribution')
    axes[1].legend()
    plt.tight_layout()
    plt.show()

def evaluate_anomaly_detection(y_true, y_pred, scores):
    """
    评估异常检测性能
    :param y_true: 真实标签（1正常，-1异常）
    :param y_pred: 预测标签
    :param scores: 异常得分
    :return: 分类报告, AUC
    """
    # 转换标签为0/1格式
    y_true_binary = (y_true == -1).astype(int)
    y_pred_binary = (y_pred == -1).astype(int)

    print("Classification Report:")
    print(classification_report(y_true_binary, y_pred_binary,
                                target_names=['Normal', 'Anomaly']))

    auc = roc_auc_score(y_true_binary, scores)

    return auc

def plot_roc_curve(y_true, scores):
    """
    绘制ROC曲线
    :param y_true: 真实标签（1正常，-1异常）
    :param scores: 异常得分
    """
    y_true_binary = (y_true == -1).astype(int)

    fpr, tpr, thresholds = roc_curve(y_true_binary, scores)
    roc_auc = roc_auc_score(y_true_binary, scores)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, 'b-', label=f'ROC curve (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], 'r--', label='Random')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve - Anomaly Detection')
    plt.legend()
    plt.show()

    return roc_auc

def contamination_sensitivity_analysis(X, y, contamination_range):
    """
    污染率敏感性分析
    :param X: 特征矩阵
    :param y: 真实标签
    :param contamination_range: 污染率范围
    :return: 各污染率下的性能指标
    """
    from sklearn.metrics import f1_score, precision_score, recall_score

    f1_scores = []
    precisions = []
    recalls = []

    for cont in contamination_range:
        _, labels, _ = isolation_forest_anomaly_detection(X, contamination=cont)

        y_binary = (y == -1).astype(int)
        y_pred_binary = (labels == -1).astype(int)

        f1 = f1_score(y_binary, y_pred_binary)
        prec = precision_score(y_binary, y_pred_binary, zero_division=0)
        rec = recall_score(y_binary, y_pred_binary, zero_division=0)

        f1_scores.append(f1)
        precisions.append(prec)
        recalls.append(rec)

    plt.figure(figsize=(10, 6))
    plt.plot(contamination_range, f1_scores, 'o-', label='F1 Score')
    plt.plot(contamination_range, precisions, 's-', label='Precision')
    plt.plot(contamination_range, recalls, '^-', label='Recall')
    plt.xlabel('Contamination Rate')
    plt.ylabel('Score')
    plt.title('Sensitivity Analysis: Contamination Rate')
    plt.legend()
    plt.show()

    return f1_scores, precisions, recalls
```

---

## 机器学习算法选择指南

### 按问题类型选择

| 问题类型 | 推荐算法 | 说明 |
|---------|---------|------|
| 二分类（中小规模） | 逻辑回归、SVM、朴素贝叶斯 | 快且强；SVM 需调参 |
| 二分类（大数据） | 逻辑回归、随机森林 | 逻辑回归快，RF 鲁棒 |
| 多分类 | 随机森林、逻辑回归(softmax)、决策树 | RF 通用；可解释选决策树 |
| 回归 | 随机森林、AdaBoost | 参考 02 §3 线性回归 / §9 XGBoost |
| 文本分类 | 朴素贝叶斯(Multinomial)、逻辑回归 | 词频特征下 NB 是强基线 |
| 异常检测 | 孤立森林 | 无监督检测 |
| 特征选择 | 随机森林、决策树 | 特征重要性 |
| 高维数据 | 随机森林、SVM(线性核) | RF 特征随机选择；先 PCA 降维 |
| 不平衡数据 | AdaBoost、随机森林(class_weight) | 可调整权重 |

### 按数据规模选择

| 数据规模 | 推荐算法 | 理由 |
|---------|---------|------|
| 小样本（≤10³） | 朴素贝叶斯、SVM、逻辑回归 | 参数少方差小，SVM 小样本泛化强 |
| 中等规模（10³~10⁵） | 逻辑回归、决策树、KNN、SVM | 全部秒级训练，交叉验证选优 |
| 大规模（>10⁵） | 逻辑回归、随机森林、XGBoost | KNN/SVM 预测/训练慢，避开 |

### 按数据特征选择

| 数据特征 | 推荐算法 |
|---------|---------|
| 含缺失值 | 随机森林、XGBoost |
| 高维度 | 随机森林、SVM(线性核) |
| 特征量纲差异大 | 任意（须先标准化，尤其 KNN/SVM） |
| 非线性关系 | 随机森林、SVM(RBF)、AdaBoost |
| 需要概率输出 | 逻辑回归、随机森林 |
| 噪声较多 | 随机森林 |
| 强相关特征 | 逻辑回归(L2)、随机森林（NB 会低估概率） |

### 按解释性要求选择

| 解释性要求 | 推荐算法 |
|-----------|---------|
| 需要特征重要性 | 随机森林、AdaBoost |
| 需要决策规则 | 决策树（单棵树可视化） |
| 需要系数解读 | 逻辑回归（系数即特征影响） |
| 需要预测概率 | 逻辑回归、随机森林 |
| 黑箱可接受 | 所有集成学习 |

---

## 参考文献

1. Breiman, L. (2001). Random Forests. *Machine Learning*, 45(1), 5-32.
2. Freund, Y., & Schapire, R. E. (1997). A decision-theoretic generalization of on-line learning and an application to boosting. *Journal of Computer and System Sciences*, 55(1), 119-139.
3. Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). Isolation Forest. *Proceedings of the 2008 Eighth IEEE International Conference on Data Mining (ICDM)*, 413-422.
4. Breiman, L., Friedman, J., Stone, C. J., & Olshen, R. A. (1984). *Classification and Regression Trees*. Wadsworth.
5. Friedman, J. H. (2001). Greedy Function Approximation: A Gradient Boosting Machine. *Annals of Statistics*, 29(5), 1189-1232.
6. Cortes, C., & Vapnik, V. (1995). Support Vector Networks. *Machine Learning*, 20(3), 273-297.
7. Cover, T. M., & Hart, P. E. (1967). Nearest neighbor pattern classification. *IEEE Transactions on Information Theory*, 13(1), 21-27.
8. Rish, I. (2001). An empirical study of the naive Bayes classifier. *IJCAI Workshop on Empirical Methods in AI*.
9. Hosmer, D. W., Lemeshow, S., & Sturdivant, R. X. (2013). *Applied Logistic Regression* (3rd ed.). Wiley.
10. Quinlan, J. R. (1986). Induction of Decision Trees. *Machine Learning*, 1(1), 81-106.
11. Hastie, T., Tibshirani, R., & Friedman, J. (2009). *The Elements of Statistical Learning* (2nd ed.). Springer.
