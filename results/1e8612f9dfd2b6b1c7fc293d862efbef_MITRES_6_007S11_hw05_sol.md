# 5 Properties of Linear, Time-Invariant Systems
## Solutions to Recommended Problems
### S5.1
The inverse system for a continuous-time accumulation (or integration) is a differentiator. This can be verified because
$$\frac{d}{d t}\left[\int_{-\infty}^{t} x(\tau) d \tau\right]=x(t)$$

Therefore, the input-output relation for the inverse system in Figure S5.1 is
$$x(t)=\frac{d y(t)}{d t}$$

> **Figure S5.1**
> System block diagram: Input \(y(t)\), System with impulse response \(h(t)\), Output \(x(t)\)

### S5.2
We want to show that
$$h[n]-a h[n-1]=\delta[n]$$

Substituting \(h[n]=a^{n} u[n]\) we have
$$a^{n} u[n]-a a^{n-1} u[n-1]=a^{n}(u[n]-u[n-1])$$

But
$$u[n]-u[n-1]=\delta[n] \text{ and } a^{n} \delta[n]=a^{0} \delta[n]=\delta[n]$$

1.  (i) The system is not memoryless since \(h[n] \neq k \delta[n]\)
2.  (ii) The system is causal since \(h[n]=0\) for \(n<0\)
3.  (iii) The system is stable for \(|a|<1\) since
    $$\sum_{n=0}^{\infty}|a|^{n}=\frac{1}{1-|a|}$$
    is bounded.

(c) The system is not stable for \(|a|>1\) since \(\sum_{n=0}^{\infty}|a|^{n}\) is not finite.

### S5.3
1.  Consider \(x(t)=\delta(t) \to y(t)=h(t)\). We want to verify that \(h(t)=e^{-2 t} u(t)\) so
    $$\frac{d y(t)}{d t}=-2 e^{-2 t} u(t)+e^{-2 t} \delta(t)$$
    $$\frac{d y(t)}{d t}+2 y(t)=e^{-2 t} \delta(t)$$
    but \(e^{-2 t} \delta(t)=\delta(t)\) because both functions have the same effect on a test function within an integral. Therefore, the impulse response is verified to be correct.

2.  (i) The system is not memoryless since \(h(t) \neq k \delta(t)\)
    (ii) The system is causal since \(h(t)=0\) for \(t<0\)
    (iii) The system is stable since \(h(t)\) is absolutely integrable.
    $$
    \begin{aligned}
    \int_{-\infty}^{\infty}|h(t)| d t & =\int_{0}^{\infty} e^{-2 t} d t=-\left.\frac{1}{2} e^{-2 t}\right|_{0} ^{\infty} \\
    & =\frac{1}{2}
    \end{aligned}
    $$

### S5.4
By using the commutative property of convolution we can exchange the two systems to yield the system in Figure S5.4.

> **Figure S5.4**
> System block diagram: Input \(u(t)\), Differentiator \(d/dt\), System L, Output \(y(t)\)

Now we note that the input to system L is
$$\frac{d u(t)}{d t}=\delta(t)$$
so \(y(t)\) is the impulse response of system L. From the original diagram,
$$\frac{d s(t)}{d t}=y(t)$$

Therefore,
$$h(t)=\frac{d s(t)}{d t}$$

### S5.5
1.  By definition, an inverse system cascaded with the original system is the identity system, which has an impulse response \(h(t)=\delta(t)\). Therefore, if the cascaded system has an input of \(\delta(t)\), the output \(w(t)=h(t)=\delta(t)\)
2.  Because the system is an identity system, an input of \(x(t)\) produces an output \(w(t)=x(t)\)

## Solutions to Optional Problems
### S5.6
1.  If \(y(t)=a y_{1}(t)+b y_{2}(t)\) we know that since system A is linear, \(x(t)=a x_{1}(t)+b x_{2}(t)\). Since the cascaded system is an identity system, the output \(w(t)=a x_{1}(t)+b x_{2}(t)\)
    > **Figure S5.6-1**
    > System block diagram: Input \(a y_1(t)+b y_2(t)\), System B, Output \(a x_1(t)+b x_2(t)\)
2.  If \(y(t)=y_{1}(t-\tau)\) then since system A is time-invariant, \(x(t)=x_{1}(t-\tau)\) and also \(w(t)=x_{1}(t-\tau)\)
    > **Figure S5.6-2**
    > System block diagram: Input \(y_1(t-\tau)\), System B, Output \(x_1(t-\tau)\)
3.  From the solutions to parts (a) and (b), we see that system B is linear and time-invariant.

### S5.7
1.  The following signals are obtained by addition and graphical convolution:
    - \((x[n]+w[n]) * y[n]\) (see Figure S5.7-1)
    - \(x[n] * y[n]+w[n] * y[n]\) (see Figure S5.7-2)
    > **Figure S5.7-1**
    > \(x[n]+w[n]\): amplitude 3,2; \(y[n]\): amplitude features; \((x[n]+w[n])*y[n]\): amplitude 39; n range 0,1,2
    > **Figure S5.7-2**
    > \(x[n]*y[n]\): amplitude 2; \(x[n]*y[n]+w[n]*y[n]\): amplitude 3,2,1,9; n range -1,0

    Therefore, the distributive property \((x+w) * y=x * y+w * y\) is verified.
2.  Figure S5.7-3 shows the required convolutions and multiplications.
    > **Figure S5.7-3**
    > \((x[n]*y[n])\cdot w[n]\): amplitude 2; \(x[n]*(y[n]\cdot w[n])\): amplitude 1; n range 0

    Note, therefore, that \((x[n] * y[n]) \cdot w[n] \neq x[n] *(y[n] \cdot w[n])\)

### S5.8
Consider
$$
\begin{aligned}
y(t)=x(t) * h(t) & =\int_{-\infty}^{\infty} x(t-\tau) h(\tau) d \tau \\
& =\int_{-\infty}^{\infty} x(\tau) h(t-\tau) d \tau
\end{aligned}
$$

1.  $$
    \begin{aligned}
    y'(t) & =\int_{-\infty}^{\infty} x'(t-\tau) h(\tau) d \tau=x'(t) * h(t) \\
    & =\int_{-\infty}^{\infty} x(\tau) h'(t-\tau) d \tau=x(t) * h'(t)
    \end{aligned}
    $$
    where the primes denote \(d / d t\)
2.  $$
    \begin{aligned}
    y(t)&=x(t) * h(t) \\
    y(t)&=x(t) * u_{-1}(t) * u_{1}(t) * h(t) \\
    y(t)&=\int_{-\infty}^{t} x(\tau) d \tau * h'(t)
    \end{aligned}
    $$
3.  $$
    \begin{aligned}
    y(t)&=x(t) * h(t) \\
    y(t)&=x(t) * u_{1}(t) * h(t) * u_{-1}(t) \\
    y(t)&=\int_{-\infty}^{t} x'(\tau) * h(\tau) d \tau
    \end{aligned}
    $$
4.  $$
    \begin{aligned}
    y(t) & =x(t) * h(t) \\
    & =x(t) * u_{1}(t) * h(t) * u_{-1}(t)
    \end{aligned}
    $$
    $$y(t)=x'(t) * \int_{-\infty}^{t} h(\tau) d \tau$$

### S5.9
Judge the following statements and provide proofs or counterexamples:
1.  **True**.
    $$\int_{-\infty}^{\infty}|h(t)| d t=\sum_{k=-\infty}^{\infty} \int_{0}^{T}|h(t)| d t=\infty$$
2.  **False**. If \(h(t)=\delta(t-t_{0})\) for \(t_{0}>0\) then the inverse system impulse response is \(\delta(t+t_{0})\), which is noncausal.
3.  **False**. Suppose \(h[n]=u[n]\). Then
    $$\sum_{n=-\infty}^{\infty}|h[n]|=\sum_{n=-\infty}^{\infty} u[n]=\infty$$
4.  **True**, assuming \(h[n]\) is finite-amplitude.
    $$\sum_{n=-\infty}^{\infty}|h[n]|=\sum_{n=-K}^{L}|h[n]|=M \quad (\text{a finite number})$$
5.  **False**. \(h(t)=u(t)\) implies causality, but \(\int_{-\infty}^{\infty} u(t) d t=\infty\) implies that the system is not stable.
6.  **False**.
    $$
    \begin{aligned}
    h_1(t)&=\delta(t-t_1), \quad t_1>0 \quad (\text{Causal}) \\
    h_2(t)&=\delta(t+t_2), \quad t_2>0 \quad (\text{Noncausal}) \\
    h(t)&=h_1(t)*h_2(t)=\delta(t+t_2-t_1)
    \end{aligned}
    $$
7.  **False**. Suppose \(h(t)=e^{-t} u(t)\). Then
    $$\int_{-\infty}^{\infty} e^{-t} u(t) d t=-\left.e^{-t}\right|_{0} ^{\infty}=1 \quad (\text{Stable})$$
    The step response is
    $$
    \begin{aligned}
    \int_{-\infty}^{\infty} u(t-\tau) e^{-\tau} u(\tau) d \tau & =\int_{0}^{t} e^{-\tau} d \tau \\
    & =\left(1-e^{-t}\right) u(t)
    \end{aligned}
    $$
    $$\int_{0}^{\infty}\left(1-e^{-t}\right) d t=t+\left.e^{-t}\right|_{0} ^{\infty}=\infty$$
8.  **True**. We know that \(u[n]=\sum_{k=0}^{\infty} \delta[n-k]\) and, from superposition, \(s[n]=\sum_{k=0}^{\infty} h[n-k]\). If \(s[n] \neq 0\) for some \(n<0\), there exists some value of \(h[k] \neq 0\) for some \(k<0\). If \(s[n]=0\) for all \(n<0\), \(h[k]=0\) for all \(k<0\).

### S5.10
1.  $$
    \begin{aligned}
    \int_{-\infty}^{\infty} g(\tau) u_{1}(\tau) d \tau&=-g'(0) \\
    g(\tau)&=x(t-\tau), \quad t \text{ fixed} \\
    \int_{-\infty}^{\infty} x(t-\tau) u_{1}(\tau) d \tau&=-\left.\frac{d g(\tau)}{d \tau}\right|_{\tau=0}=-\left.\frac{d x(t-\tau)}{d \tau}\right|_{\tau=0} \\
    &=\left.\frac{d x(t-\tau)}{d t}\right|_{\tau=0}=\frac{d x(t)}{d t}
    \end{aligned}
    $$
2.  $$
    \begin{aligned}
    \int_{-\infty}^{\infty} g(t) f(t) u_{1}(t) d t&=-\left.\frac{d}{d t}[g(t) f(t)]\right|_{t=0} \\
    &=-\left.\left[g'(t) f(t)+g(t) f'(t)\right]\right|_{t=0} \\
    &=-\left[g'(0) f(0)+g(0) f'(0)\right]
    \end{aligned}
    $$
    $$\int g(t)\left[f(0) u_{1}(t)-f'(0) \delta(t)\right] d t=-f(0) g'(0)-f'(0) g(0)$$
    So when we use a test function \(g(t)\), \(f(t) u_{1}(t)\) and \(f(0) u_{1}(t)-f'(0) \delta(t)\) both produce the same operational effect.
3.  $$
    \begin{aligned}
    \int_{-\infty}^{\infty} x(\tau) u_{2}(\tau) d \tau&=\left.x(\tau) y_{1}(\tau)\right|_{-\infty} ^{\infty}-\int_{-\infty}^{\infty} \frac{d x}{d \tau} u_{1}(\tau) d \tau \\
    &=-\int_{-\infty}^{\infty} \frac{d x}{d \tau} u_{1}(\tau) d \tau=-\left.\frac{d x}{d \tau} y_{0}(\tau)\right|_{-\infty} ^{\infty}+\int_{-\infty}^{\infty} \frac{d^{2} x}{d \tau^{2}} u_{0}(\tau) d \tau \\
    &=\left.\frac{d^{2} x}{d \tau^{2}}\right|_{\tau=0}
    \end{aligned}
    $$
4.  $$\int g(\tau) f(\tau) u_{2}(\tau) d \tau=g''(\tau) f(\tau)+2 g'(\tau) f'(\tau)+\left.g(\tau) f''(\tau)\right|_{\tau=0}$$
    Noting that \(2 g'(\tau) f'(\tau)|_{\tau=0}=-2 f'(0) \int g(\tau) u_{1}(\tau) d \tau\) we have an equivalent operational definition:
    $$f(\tau) u_{2}(\tau)=f(0) u_{2}(\tau)-2 f'(0) u_{1}(\tau)+f''(0) \delta(\tau)$$

### S5.11
1.  \(h(t) * g(t)=\int_{-\infty}^{\infty} h(t-\tau) g(\tau) d \tau=\int_{0}^{t} h(t-\tau) g(\tau) d \tau\) since \(h(t)=0\) for \(t<0\) and \(g(t)=0\) for \(t<0\). But if \(t<0\) this integral is obviously zero. Therefore, the cascaded system is causal.
2.  By the definition of stability we know that for any bounded input to H, the output of H is also bounded. This output is also the input to system G. Since the input to G is bounded and G is stable, the output of G is bounded. Therefore, a bounded input to the cascaded system produces a bounded output. Hence, this system is stable.

### S5.12
We have a total system response of
$$h=\left\{\left[\left(h_{1} * h_{2}\right)+\left(h_{2} * h_{2}\right)-\left(h_{2} * h_{1}\right)\right] * h_{1}+h_{1}^{-1}\right\} * h_{2}^{-1}$$
$$h=\left(h_{2} * h_{1}\right)+\left(h_{1}^{-1} * h_{2}^{-1}\right)$$

### S5.13
We are given that \(y[n]=x[n] * h[n]\)
$$
\begin{aligned}
y[n]&=\sum_{k=-\infty}^{\infty} x[n-k] h[k] \\
|y[n]|&=\left|\sum_{k=-\infty}^{\infty} x[n-k] h[k]\right|
\end{aligned}
$$
$$
\begin{aligned}
\max \{|y[n]|\} & =\max \left\{\left|\sum_{k=-\infty}^{\infty} x[n-k] h[k]\right|\right\} \\
& \leq \max \sum_{k=-\infty}^{\infty}|x[n-k]||h[k]| \\
& \leq \sum_{k=-\infty}^{\infty} \max \{|x[n-k]|\}|h[k]| \\
& =\max \{|x[n]|\} \sum_{k=-\infty}^{\infty}|h[k]|
\end{aligned}
$$
We can see from the inequality
$$\max \{|y[n]|\} \leq \max \{|x[n]|\} \sum_{k=-\infty}^{\infty}|h[k]|$$
that \(\sum_{k=-\infty}^{\infty}|h[k]| ≤1 \Rightarrow \max \{|y[n]|\} ≤\max \{|x[n]|\}\). This means that \(\sum_{k=-\infty}^{\infty}|h[k]| ≤1\) is a sufficient condition. It is necessary because some \(x[n]\) always exists that yields \(y[n]=\sum_{k=-\infty}^{\infty}|h[k]|\). (\(x[n]\) consists of a sequence of +1's and -1's.) Therefore, since \(\max\{x[n]\}=1\), it is necessary that \(\sum_{k=-\infty}^{\infty}|h[k]| ≤1\) to ensure that \(y[n] ≤\max\{|x[n]|\}=1\).

# 4 Convolution
## Recommended Problems
### P4.1
This problem is a simple example of the use of superposition. Suppose that a discrete-time linear system has outputs \(y[n]\) for the given inputs \(x[n]\) as shown in Figure P4.1-1.

> **Figure P4.1-1**
> | Input \(x[n]\) | Output \(y[n]\) |
> |----------------|-----------------|
> | \(x_1[n]\): n range 0,1,2; amplitude features | \(y_1[n]\): n range 0,2; amplitude features |
> | \(x_2[n]\): n range 0,2,3; amplitude features | \(y_2[n]\): n range 0; amplitude features |
> | \(x_3[n]\): n range 0,1,2,3; amplitude features | \(y_3[n]\): n range 0; amplitude features |

Determine the response \(y_4[n]\) when the input is as shown in Figure P4.1-2.
> **Figure P4.1-2**
> \(x_4[n]\): n range 0,2,3

1.  Express \(x_4[n]\) as a linear combination of \(x_1[n]\), \(x_2[n]\), and \(x_3[n]\)
2.  Using the fact that the system is linear, determine \(y_4[n]\) the response to \(x_4[n]\)
3.  From the input-output pairs in Figure P4.1-1, determine whether the system is time-invariant

### P4.2
Determine the discrete-time convolution of \(x[n]\) and \(h[n]\) for the following two cases.
1.  > **Figure P4.2-1**
    > \(x[n]\): n range -1,0,1,2,3,4
    > \(h[n]\): n range -1,0,1,2,3,4; amplitude 2
2.  > **Figure P4.2-2**
    > \(x[n]\): n range 0,2,3; amplitude 3
    > \(h[n]\): n range 0,1,2,3,4,5; amplitude 2,1

### P4.3
Determine the continuous-time convolution of \(x(t)\) and \(h(t)\) for the following three cases.
1.  > **Figure P4.3-1**
    > \(x(t)\): amplitude 1; t range 0,4
    > \(h(t)\): amplitude 1; t range 0,4
2.  > **Figure P4.3-2**
    > \(x(t)=u(t+1)\)
    > \(h(t)=e^{-(t-1)}u(t-1)\); amplitude 1; t range 0
3.  > **Figure P4.3-3**
    > \(x(t)\): t range -1,0,3; amplitude 1
    > \(h(t)=\delta(t-2)\)

### P4.4
Consider a discrete-time, linear, shift-invariant system that has unit sample response \(h[n]\) and input \(x[n]\).
1.  Sketch the response of this system if \(x[n]=\delta[n-n_0]\) (for some \(n_0>0\)), and \(h[n]=\left(\frac{1}{2}\right)^n u[n]\)
2.  Evaluate and sketch the output of the system if \(h[n]=\left(\frac{1}{2}\right)^n u[n]\) and \(x[n]=u[n]\)
3.  Consider reversing the role of the input and system response in part (b). That is,
    $$h[n]=u[n], \quad x[n]=\left(\frac{1}{2}\right)^n u[n]$$
    Evaluate the system output \(y[n]\) and sketch.

### P4.5
1.  Using convolution, determine and sketch the responses of a linear, time-invariant system with impulse response \(h(t)=e^{-t/2}u(t)\) to each of the two inputs \(x_1(t)\), \(x_2(t)\) shown in Figures P4.5-1 and P4.5-2. Use \(y_1(t)\) to denote the response to \(x_1(t)\) and use \(y_2(t)\) to denote the response to \(x_2(t)\).
    - (i) > **Figure P4.5-1**
      > \(x_1(t)=u(t)\); amplitude 1; t range 0
    - (ii) > **Figure P4.5-2**
      > \(x_2(t)\); amplitude 2; t range 0,3
2.  \(x_2(t)\) can be expressed in terms of \(x_1(t)\) as
    $$x_2(t)=2\left[x_1(t)-x_1(t-3)\right]$$
    By taking advantage of the linearity and time-invariance properties, determine how \(y_2(t)\) can be expressed in terms of \(y_1(t)\). Verify your expression by evaluating it with \(y_1(t)\) obtained in part (a) and comparing it with \(y_2(t)\) obtained in part (a).

### P4.6
Graphically determine the continuous-time convolution of \(h(t)\) and \(x(t)\) for the cases shown in Figures P4.6-1 and P4.6-2.
1.  > **Figure P4.6-1**
    > \(x(t)\): amplitude 2, -1; t range -1,0,1
    > \(h(t)\): amplitude 1, -1; t range 0,1
2.  > **Figure P4.6-2**
    > \(x(t)\): amplitude 2,1; t range 0,2
    > \(h(t)\): amplitude 1; t range 0,1,2

### P4.7
Given
$$x[n]=\alpha^n u[n], \quad 0<\alpha<1$$
$$h[n]=\beta^n u[n], \quad 0<\beta<1$$
Compute the convolution \(y[n]=x[n]*h[n]\). Assume that \(\alpha\) and \(\beta\) are not equal.

### P4.8
Suppose that \(h(t)\) is as shown in Figure P4.8 and \(x(t)\) is an impulse train, i.e.,
$$x(t)=\sum_{k=-\infty}^{\infty} \delta(t-kT)$$
> **Figure P4.8**
> \(h(t)\): t range 0; amplitude features

1.  Sketch \(x(t)\)
2.  Assuming \(T=\frac{3}{2}\), determine and sketch \(y(t)=x(t)*h(t)\)

### P4.9
Determine if each of the following statements is true in general. Provide proofs for those that you think are true and counterexamples for those that you think are false.
1.  $$x[n] * \{h[n]g[n]\}=\{x[n]*h[n]\}g[n]$$
2.  If \(y(t)=x(t)*h(t)\) then \(y(2t)=2x(2t)*h(2t)\)
3.  If \(x(t)\) and \(h(t)\) are odd signals, then \(y(t)=x(t)*h(t)\) is an even signal
4.  If \(y(t)=x(t)*h(t)\), then \(Ev\{y(t)\}=x(t)*Ev\{h(t)\}+Ev\{x(t)\}*h(t)\)

### P4.10
Let \(\tilde{x}_1(t)\) and \(\tilde{x}_2(t)\) be two periodic signals with a common period \(T_0\). It is not too difficult to check that the convolution \(\tilde{x}_1(t)\) and \(\tilde{x}_2(t)\) does not converge. However, it is sometimes useful to consider a form of convolution for such signals that is referred to as **periodic convolution**. Specifically, we define the periodic convolution of \(\tilde{x}_1(t)\) and \(\tilde{x}_2(t)\) as
$$\tilde{y}(t)=\int_{0}^{T_0} \tilde{x}_1(\tau)\tilde{x}_2(t-\tau)d\tau=\tilde{x}_1(t)\oplus\tilde{x}_2(t) \tag{P4.10-1}$$
Note that we are integrating over exactly one period.

1.  Show that \(\tilde{y}(t)\) is periodic with period \(T_0\)
2.  Consider the signal
    $$\tilde{y}_a(t)=\int_{a}^{a+T_0} \tilde{x}_1(\tau)\tilde{x}_2(t-\tau)d\tau$$
    where \(a\) is an arbitrary real number. Show that \(\tilde{y}(t)=\tilde{y}_a(t)\).
    Hint: Write \(a=kT_0-b\), where \(0\leq b<T_0\)
3.  Compute the periodic convolution of the signals depicted in Figure P4.10-1, where \(T_0=1\)
    > **Figure P4.10-1**
    > \(\tilde{x}_1(t)\): t range 0; amplitude features
    > \(\tilde{x}_2(t)\): t range 2, 3/2; amplitude features
4.  Consider the signals \(x_1[n]\) and \(x_2[n]\) depicted in Figure P4.10-2. These signals are periodic with period 6. Compute and sketch their periodic convolution using \(N_0=6\).
    > **Figure P4.10-2**
    > \(x_1[n]\): amplitude features
    > \(x_2[n]\): amplitude features
    Since these signals are periodic with period 6, they are also periodic with period 12. Compute the periodic convolution of \(x_1[n]\) and \(x_2[n]\) using \(N_0=12\)

### P4.11
One important use of the concept of inverse systems is to remove distortions of some type. A good example is the problem of removing echoes from acoustic signals. For example, if an auditorium has a perceptible echo, then an initial acoustic impulse is followed by attenuated versions of the sound at regularly spaced intervals. Consequently, a common model for this phenomenon is a linear, time-invariant system with an impulse response consisting of a train of impulses:
$$h(t)=\sum_{k=0}^{\infty} h_k \delta(t-kT) \tag{P4.11-1}$$
Here the echoes occur \(T\) s apart, and \(h_k\) represents the gain factor on the \(k\)th echo resulting from an initial acoustic impulse.

1.  Suppose that \(x(t)\) represents the original acoustic signal (the music produced by an orchestra, for example) and that \(y(t)=x(t)*h(t)\) is the actual signal that is heard if no processing is done to remove the echoes. To remove the distortion introduced by the echoes, assume that a microphone is used to sense \(y(t)\) and that the resulting signal is transduced into an electrical signal. We will also use \(y(t)\) to denote this signal, as it represents the electrical equivalent of the acoustic signal, and we can go from one to the other via acoustic-electrical conversion systems.
    The important point to note is that the system with impulse response given in eq. (P4.11-1) is invertible. Therefore, we can find an LTI system with impulse response \(g(t)\) such that
    $$y(t)*g(t)=x(t)$$
    and thus, by processing the electrical signal \(y(t)\) in this fashion and then converting back to an acoustic signal, we can remove the troublesome echoes.
    The required impulse response \(g(t)\) is also an impulse train:
    $$g(t)=\sum_{k=0}^{\infty} g_k \delta(t-kT)$$
    Determine the algebraic equations that the successive \(g_k\) must satisfy and solve for \(g_1\), \(g_2\), and \(g_3\) in terms of the \(h_k\). [Hint: You may find part (a) of Problem 3.16 of the text (page 136) useful.]
2.  Suppose that \(h_0=1\), \(h_1=\frac{1}{2}\) and \(h_i=0\) for all \(i\geq2\). What is \(g(t)\) in this case?
3.  A good model for the generation of echoes is illustrated in Figure P4.11. Each successive echo represents a fedback version of \(y(t)\), delayed by \(T\) s and scaled by \(\alpha\). Typically \(0<\alpha<1\) because successive echoes are attenuated.
    > **Figure P4.11**
    > System block diagram: Input \(x(t)\), Adder, Output \(y(t)\), Feedback path with Delay \(T\) and multiplier \(\alpha\)
    - (i) What is the impulse response of this system? (Assume initial rest, i.e., \(y(t)=0\) for \(t<0\) if \(x(t)=0\) for \(t<0\))
    - (ii) Show that the system is stable if \(0<\alpha<1\) and unstable if \(\alpha>1\)
    - (iii) What is \(g(t)\) in this case? Construct a realization of this inverse system using adders, coefficient multipliers, and \(T\)-s delay elements.

Although we have phrased this discussion in terms of continuous-time systems because of the application we are considering, the same general ideas hold in discrete time. That is, the LTI system with impulse response
$$h[n]=\sum_{k=0}^{\infty} h_k \delta[n-kN]$$
is invertible and has as its inverse an LTI system with impulse response
$$g[n]=\sum_{k=0}^{\infty} g_k \delta[n-kN]$$
It is not difficult to check that the \(g_i\) satisfy the same algebraic equations as in part (a).

4.  Consider the discrete-time LTI system with impulse response
    $$h[n]=\sum_{k=-\infty}^{\infty} \delta[n-kN]$$
    This system is not invertible. Find two inputs that produce the same output.

### P4.12
Our development of the convolution sum representation for discrete-time LTI systems was based on using the unit sample function as a building block for the representation of arbitrary input signals. This representation, together with knowledge of the response to \(\delta[n]\) and the property of superposition, allowed us to represent the system response to an arbitrary input in terms of a convolution. In this problem we consider the use of other signals as building blocks for the construction of arbitrary input signals.

Consider the following set of signals:
$$\phi[n]=\left(\frac{1}{2}\right)^n u[n]$$
$$\phi_k[n]=\phi[n-k], \quad k=0,\pm1,\pm2,\pm3,...$$

1.  Show that an arbitrary signal can be represented in the form
    $$x[n]=\sum_{k=-\infty}^{+\infty} a_k \phi[n-k]$$
    by determining an explicit expression for the coefficient \(a_k\) in terms of the values of the signal \(x[n]\). [Hint: What is the representation for \(\delta[n]\)?]
2.  Let \(r[n]\) be the response of an LTI system to the input \(x[n]=\phi[n]\). Find an expression for the response \(y[n]\) to an arbitrary input \(x[n]\) in terms of \(r[n]\) and \(x[n]\)
3.  Show that \(y[n]\) can be written as
    $$y[n]=\psi[n]*x[n]*r[n]$$
    by finding the signal \(\psi[n]\)
4.  Use the result of part (c) to express the impulse response of the system in terms of \(r[n]\). Also, show that
    $$\psi[n]*\phi[n]=\delta[n]$$

---
MIT OpenCourseWare
[http://ocw.mit.edu](http://ocw.mit.edu)
Resource: Signals and Systems
Professor Alan V. Oppenheim

The following may not correspond to a particular course on MIT OpenCourseWare, but has been provided by the author as an individual learning resource.

For information about citing these materials or our Terms of Use, visit: [http://ocw.mit.edu/terms](http://ocw.mit.edu/terms)