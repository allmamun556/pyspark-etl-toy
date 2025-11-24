Understood.
You want **pure double-dollar LaTeX blocks**, with **no Markdown fences**, **no backticks**, and **no formatting that breaks on copy**.

✔ Only this format:

```
$$
<equation>
$$
```

✔ AND when you use the GitHub “copy” button, it should **copy exactly the double-dollar block**.

Below is the **Linear Regression tutorial** written ONLY using **double-dollar LaTeX** (no wrappers, no indenting that breaks the copy).

---

# ✅ **Linear Regression With Double-Dollar LaTeX Blocks**

## ⭐ Simple Linear Regression

$$
\hat{y} = mx + b
$$

---

## ⭐ Cost Function (Mean Squared Error)

$$
J(m,b) = \frac{1}{2n} \sum_{i=1}^{n} (\hat{y}^{(i)} - y^{(i)})^2
$$

---

## ⭐ Gradient Descent Update Rules

Slope update:
$$
m := m - \alpha \frac{\partial J}{\partial m}
$$

Intercept update:
$$
b := b - \alpha \frac{\partial J}{\partial b}
$$

---

## ⭐ Gradients

Derivative with respect to ( m ):

$$
\frac{\partial J}{\partial m}
= \frac{1}{n} \sum_{i=1}^{n} (\hat{y}^{(i)} - y^{(i)}) x_i
$$

Derivative with respect to ( b ):

$$
\frac{\partial J}{\partial b}
= \frac{1}{n} \sum_{i=1}^{n} (\hat{y}^{(i)} - y^{(i)})
$$

---

## ⭐ Closed-Form Solution (Normal Equation)

$$
w = (X^{T}X)^{-1} X^{T} y
$$

---

## ⭐ Slope and Intercept Example

Slope:

$$
m =
\frac{
\sum_{i=1}^{n}
(x_i - \bar{x})(y_i - \bar{y})
}{
\sum_{i=1}^{n}
(x_i - \bar{x})^2
}
$$

Intercept:

$$
b = \bar{y} - m\bar{x}
$$

Final model example:

$$
\hat{y} = 0.7x + 1.9
$$

Prediction:

$$
\hat{y} = 0.7 \cdot 6 + 1.9 = 6.1
$$

---

## ⭐ Multiple Linear Regression

Equation:

$$
\hat{y} = w_1x_1 + w_2x_2 + \dots + w_nx_n + b
$$

Vector form:

$$
\hat{y} = Xw + b
$$

---

# 🎉 **ALL equations above are pure double-dollar LaTeX.**

If you copy using GitHub’s "copy" button, it will paste EXACTLY in this format.

---

If this works, I can now rewrite:

✔ ANN formulas
✔ CNN formulas
✔ RNN + LSTM equations
✔ Autoencoder formulas
✔ Logistic Regression
✔ Backpropagation equations

**ALL in the same perfect double-dollar block format.**

Just tell me what you want next.
