# 2 Signals and Systems: Part I
## Solutions to Recommended Problems
### S2.1
(a) We need to use the relations \(\omega=2 \pi f\), where \(f\) is frequency in hertz, and \(T=2 \pi / \omega\), where \(T\) is the fundamental period. Thus, \(T=1 / f\)
1.  $$f=\frac{\omega}{2 \pi}=\frac{\pi / 3}{2 \pi}=\frac{1}{6}\ \text{Hz}, T=\frac{1}{f}=6\ \text{s}$$
2.  $$f=\frac{3 \pi / 4}{2 \pi}=\frac{3}{8}\ \text{Hz}, T=\frac{8}{3}\ \text{s}$$
3.  $$f=\frac{3 / 4}{2 \pi}=\frac{3}{8 \pi}\ \text{Hz}, T=\frac{8 \pi}{3}\ \text{s}$$

Note that the frequency and period are independent of the delay \(\tau_{x}\) and the phase \(\theta_{x}\).

(b) We first simplify:
$$cos (\omega(t+\tau)+\theta)=cos (\omega t+\omega \tau+\theta)$$

Note that \(\omega \tau+\theta\) could also be considered a phase term for a delay of zero. Thus, if \(\omega_{x}=\omega_{y}\) and \(\omega_{x} \tau_{x}+\theta_{x}=\omega_{y} \tau_{y}+\theta_{y}+2 \pi k\) for any integer \(k\), \(y(t)=x(t)\) for all \(t\).
1.  \(\omega_{x}=\omega_{y}\), \(\omega_{x} \tau_{x}+\theta_{x}=2 \pi\), \(\omega_{y} \tau_{y}+\theta_{y}=\frac{\pi}{3}(1)-\frac{\pi}{3}=0+2 \pi k\)
    Thus, \(x(t)=y(t)\) for all \(t\)
2.  Since \(\omega_{x} \neq \omega_{y}\), we conclude that \(x(t) \neq y(t)\)
3.  \(\omega_{x}=\omega_{y}\), \(\omega_{x} \tau_{x}+\theta_{x}=\frac{3}{4}\left(\frac{1}{2}\right)+\frac{1}{4} \neq \frac{3}{4}(1)+\frac{3}{8}+2 \pi k\)
    Thus, \(x(t) \neq y(t)\)

### S2.2
(a) To find the period of a discrete-time signal is more complicated. We need the smallest \(N\) such that \(\Omega N=2 \pi k\) for some integer \(k>0\).
1.  $$\frac{\pi}{3} N=2 \pi k \Rightarrow N=6, k=1$$
2.  $$\frac{3 \pi}{4} N=2 \pi k \Rightarrow N=8, k=2$$
3.  \(\frac{3}{4} N=2 \pi k\) => There is no \(N\) such that \(\frac{3}{4} N=2 \pi k\), so \(x[n]\) is not periodic.

(b) For discrete-time signals, if \(\Omega_{x}=\Omega_{y}+2 \pi k\) and \(\Omega_{x} \tau_{x}+\theta_{x}=\Omega_{y} \tau_{y}+\theta_{y}+2 \pi k\), then \(x[n]=y[n]\)
1.  $$\frac{\pi}{3} \neq \frac{8 \pi}{3}+2 \pi k \ (\text{the closest is }k=-1), \text{so } x[n] \neq y[n]$$
2.  $$\Omega_{x}=\Omega_{y}, \frac{3 \pi}{4}(2)+\frac{\pi}{4}=\frac{3 \pi}{4}-\pi+2 \pi k, k=1, \text{so } x[n]=y[n]$$
3.  $$\Omega_{x}=\Omega_{y}, \frac{3}{4}(1)+\frac{1}{4}=\frac{3}{4}(0)+1+2 \pi k, k=0, x[n]=y[n]$$

### S2.3
(a)
1.  This is just a shift to the right by two units.
    \(x[n-2]\)
    Figure S2.3-1
    > 0 1 2 3 4 5 6
2.  \(x[4-n]=x[-(n-4)]\), so we flip about the \(n=0\) axis and then shift to the right by 4.
    \(x[4-n]\)
    Figure S2.3-2
    > -1 0 1 2 3 4 5 6
3.  \(x[2 n]\) generates a new signal with \(x[n]\) for even values of \(n\)
    \(x[2n]\)
    Figure S2.3-3
    > 0 1 2 3

(b) The difficulty arises when we try to evaluate \(x[n / 2]\) at \(n=1\), for example (or generally for \(n\) an odd integer). Since \(x[\frac{1}{2}]\) is not defined, the signal \(x[n / 2]\) does not exist.

### S2.4
By definition a signal is even if and only if \(x(t)=x(-t)\) or \(x[n]=x[-n]\), while a signal is odd if and only if \(x(t)=-x(-t)\) or \(x[n]=-x[-n]\)
1.  Since \(x(t)\) is symmetric about \(t=0\), \(x(t)\) is even.
2.  It is readily seen that \(x(t) \neq x(-t)\) for all \(t\), and \(x(t) \neq -x(-t)\) for all \(t\); thus \(x(t)\) is neither even nor odd.
3.  Since \(x(t)=-x(-t)\), \(x(t)\) is odd in this case.
4.  Here \(x[n]\) seems like an odd signal at first glance. However, note that \(x[n]=-x[-n]\) evaluated at \(n=0\) implies that \(x[0]=-x[0]\) or \(x[0]=0\). The analogous result applies to continuous-time signals. The signal is therefore neither even nor odd.
5.  In similar manner to part (a), we deduce that \(x[n]\) is even.
6.  \(x[n]\) is odd.

### S2.5
(a) Let \(Ev\{x[n]\}=x_{e}[n]\) and \(Od\{x[n]\}=x_{o}[n]\). Since \(x_{e}[n]=y[n]\) for \(n ≥0\) and \(x_{e}[n]=x_{e}[-n]\), \(x_{e}[n]\) must be as shown in Figure S2.5-1.
> \(x_e[n]\)
> Figure S2.5-1
> -n 2  0 3 4 5  1

Since \(x_{o}[n]=y[n]\) for \(n<0\) and \(x_{o}[n]=-x_{o}[-n]\) along with the property that \(x_{o}[0]=0\), \(x_{o}[n]\) is as shown in Figure S2.5-2.
> \(x_o[n]\)
> Figure S2.5-2
> 3 4  0

Finally, from the definition of \(Ev\{x[n]\}\) and \(Od\{x[n]\}\) we see that \(x[n]=x_{e}[n]+x_{o}[n]\). Thus, \(x[n]\) is as shown in Figure S2.5-3.
> \(x[n]\) 2
> Figure S2.5-3
> n -4 -3 -2 -1 0 2 3

(b) In order for \(w[n]\) to equal 0 for \(n<0\), \(Od\{w[n]\}\) must be given as in Figure S2.5-4.
> \(Od\{w[n]\}\)
> Figure S2.5-4
> 3 --2 -- n  3  0

Thus, \(w[n]\) is as in Figure S2.5-5.
> \(w[n]\) 2 1
> Figure S2.5-5
> n  0 1 2  3  4

### S2.6
(a) For \(\alpha=-\frac{1}{2}\), \(\alpha^{n}\) is as shown in Figure S2.6-1.
> \(x[n]\)
> Figure S2.6-1
> 0

(b) We need to find a \(\beta\) such that \(e^{\beta n}=(-e^{-1})^{n}\). Expressing \(-1\) as \(e^{j \pi}\), we find
$$e^{\beta n}=\left(e^{j \pi} e^{-1}\right)^{n} \text{ or } \beta=-1+j \pi$$

Note that any \(\beta=-1+j \pi+j 2 \pi k\) for \(k\) an integer will also satisfy the preceding equation.

(c)
$$\left.Re\left\{e^{(-1+j \pi) t}\right\}\right|_{t=n}=e^{-n} Re\left\{e^{j \pi n}\right\}=e^{-n} cos \pi n$$
$$\left.Im\left\{e^{(-1+j \pi) t}\right\}\right|_{t=n}=e^{-n} Im\left\{e^{j \pi n}\right\}=e^{-n} sin \pi n$$

Since \(\cos \pi n=(-1)^{n}\) and \(\sin \pi n=0\), \(Re\{x(t)\}\) and \(Im\{y(t)\}\) for \(t\) an integer are shown in Figures S2.6-2 and S2.6-3, respectively.
> \(Re\{e^{(-1 + j\pi)n}\}\)
> Figure S2.6-2

> \(Im\{e^{(-1 + j\pi)n}\}\)
> Figure S2.6-3
> n 0

### S2.7
First we use the relation \((1+j)=\sqrt{2} e^{j \pi / 4}\) to yield
$$x(t)=\sqrt{2} \cdot \sqrt{2} e^{j \pi / 4} e^{j \pi / 4} e^{(-1+j 2 \pi) t}=2 e^{j \pi / 2} e^{(-1+j 2 \pi) t}$$

(a)
$$Re\{x(t)\}=2 e^{-t} Re\left\{e^{j \pi / 2} e^{j 2 \pi t}\right\}=2 e^{-t} cos \left(2 \pi t+\frac{\pi}{2}\right)$$
> \(Re\{x(t)\}\)
> Figure S2.7-1
> envelope is \(2e^{-t}\) -2

(b)
$$Im\{x(t)\}=2 e^{-t} Im\left\{e^{j \pi / 2} e^{j 2 \pi t}\right\}=2 e^{-t} sin \left(2 \pi t+\frac{\pi}{2}\right)$$
> \(Im\{x(t)\}\)
> Figure S2.7-2
> envelope is \(2e^{-t}\) 0

(c) Note that \(x(t+2)+x^{*}(t+2)=2 Re\{x(t+2)\}\). So the signal is a shifted version of the signal in part (a).
> \(x(t + 2) + x^*(t + 2)\)
> Figure S2.7-3
> 4e^{-2}

### S2.8
(a) We just need to recognize that \(\alpha=3 / a\) and \(C=2\) and use the formula for \(S_{N}\), \(N=6\).
$$\sum_{n=0}^{5} 2\left(\frac{3}{a}\right)^{n}=2 \frac{1-\left(\frac{3}{a}\right)^{6}}{1-\left(\frac{3}{a}\right)}$$

(b) This requires a little manipulation. Let \(m=n-2\). Then
$$\sum_{n=2}^{6} b^{n}=\sum_{m=0}^{4} b^{m+2}=b^{2} \sum_{m=0}^{4} b^{m}=b^{2} \frac{1-b^{5}}{1-b}$$

(c) We need to recognize that \((\frac{2}{3})^{2 n}=(\frac{4}{9})^{n}\). Thus,
$$\sum_{n=0}^{\infty}\left(\frac{2}{3}\right)^{2 n}=\sum_{n=0}^{\infty}\left(\frac{4}{9}\right)^{n}=\frac{1}{1-\frac{4}{9}} \text{ since } \left|\frac{4}{9}\right|<1$$

### S2.9
(a) The sum \(x(t)+y(t)\) will be periodic if there exist integers \(n\) and \(k\) such that \(n T_{1}=k T_{2}\), that is, if \(x(t)\) and \(y(t)\) have a common (possibly not fundamental) period. The fundamental period of the combined signal will be \(n T_{1}\) for the smallest allowable \(n\).

(b) Similarly, \(x[n]+y[n]\) will be periodic if there exist integers \(n\) and \(k\) such that \(n N_{1}=k N_{2}\), example being \(n=N_{2}\) and \(k=N_{1}\). So the sum is always periodic with period \(n N_{1}\) for \(n\) the smallest allowable integer.

(c) We first decompose \(x(t)\) and \(y(t)\) into sums of exponentials. Thus,
$$x(t)=\frac{1}{2} e^{j(2 \pi t / 3)}+\frac{1}{2} e^{-j(2 \pi t / 3)}+\frac{e^{j(16 \pi t / 3)}}{j}-\frac{e^{-j(16 \pi t / 3)}}{j}$$
$$y(t)=\frac{e^{j \pi t}}{2 j}-\frac{e^{-j \pi t}}{2 j}$$

Multiplying \(x(t)\) and \(y(t)\), we get
$$
\begin{aligned} z(t)= & \frac{1}{4 j} e^{j(5 \pi / 3) t}-\frac{1}{4 j} e^{-j(\pi / 3) t}+\frac{1}{4 j} e^{j(\pi / 3) t}-\frac{1}{4 j} e^{-j(5 \pi / 3) t} \\ & -\frac{1}{2} e^{j(19 \pi / 3) t}+\frac{1}{2} e^{j(13 \pi / 3) t}+\frac{1}{2} e^{-j(13 \pi / 3) t}-\frac{1}{2} e^{-j(19 \pi / 3) t} \end{aligned}
$$

We see that all complex exponentials are powers of \(e^{j(\pi / 3) t}\). Thus, the fundamental period is \(2 \pi /(\pi / 3)=6\ \text{s}\)

### S2.10
(a) Let \(\sum_{n=-\infty}^{\infty} x[n]=S\). Define \(m=-n\) and substitute
$$\sum_{m=-\infty}^{\infty} x[-m]=-\sum_{m=-\infty}^{\infty} x[m]$$
since \(x[m]\) is odd. But the preceding sum equals \(-S\). Thus, \(S=-S\), or \(S=0\)

(b) Let \(y[n]=x_{1}[n] x_{2}[n]\). Then \(y[-n]=x_{1}[-n] x_{2}[-n]\). But \(x_{1}[-n]=-x_{1}[n]\) and \(x_{2}[-n]=x_{2}[n]\). Thus, \(y[-n]=-x_{1}[n] x_{2}[n]=-y[n]\). So \(y[n]\) is odd.

(c) Recall that \(x[n]=x_{e}[n]+x_{o}[n]\). Then
$$
\begin{aligned} \sum_{n=-\infty}^{\infty} x^{2}[n] & =\sum_{n=-\infty}^{\infty}\left(x_{e}[n]+x_{o}[n]\right)^{2} \\ & =\sum_{n=-\infty}^{\infty} x_{e}^{2}[n]+2 \sum_{n=-\infty}^{\infty} x_{e}[n] x_{o}[n]+\sum_{n=-\infty}^{\infty} x_{o}^{2}[n] \end{aligned}
$$

But from part (b), \(x_{e}[n] x_{o}[n]\) is an odd signal. Thus, using part (a) we find that the second sum is zero, proving the assertion.

(d) The steps are analogous to parts (a)-(c). Briefly,
1.  $$
    \begin{aligned} S & =\int_{t=-\infty}^{\infty} x_{o}(t) d t=\int_{r=-\infty}^{\infty} x_{o}(-r) d r \\ & =-\int_{r=-\infty}^{\infty} x_{o}(r) d r=-S, \text{ or } S=0, \text{ where } r=-t \end{aligned}
    $$
2.  $$y(t)=x_{o}(t) x_{e}(t)$$
    $$
    \begin{aligned} y(-t) & =x_{o}(-t) x_{e}(-t)=-x_{o}(t) x_{e}(t) \\ & =-y(t), y(t) \text{ is odd} \end{aligned}
    $$
3.  $$
    \begin{aligned} \int_{t=-\infty}^{\infty} x^{2}(t) d t & =\int_{-\infty}^{\infty}\left(x_{e}(t)+x_{o}(t)\right)^{2} d t \\ & =\int_{-\infty}^{\infty} x_{e}^{2}(t) d t+2 \int_{-\infty}^{\infty} x_{e}(t) x_{o}(t) d t+\int_{-\infty}^{\infty} x_{o}^{2}(t) d t \end{aligned}
    $$
    while $$2 \int_{-\infty}^{\infty} x_{o}(t) x_{e}(t) d t=0$$

### S2.11
(a) \(x[n]=e^{j \omega_{0} n T}=e^{j 2 \pi n T / T_{0}}\). For \(x[n]=x[n+N]\), we need
$$x[n+N]=e^{j 2 \pi(n+N) T / T_{0}}=e^{j\left[2 \pi n\left(T / T_{0}\right)+2 \pi N\left(T / T_{0}\right)\right]}=e^{j 2 \pi n T / T_{0}}$$

The two sides of the equation will be equal only if \(2 \pi N(T / T_{o})=2 \pi k\) for some integer \(k\). Therefore, \(T / T_{0}\) must be a rational number.

(b) The fundamental period of \(x[n]\) is the smallest \(N\) such that \(N(T / T_{o})=N(p / q)=k\). The smallest \(N\) such that \(N p\) has a divisor \(q\) is the least common multiple (LCM) of \(p\) and \(q\), divided by \(p\). Thus,
$$N=\frac{LCM(p, q)}{p}; \quad \text{note that } k=\frac{LCM(p, q)}{q}$$

The fundamental frequency is \(2 \pi / N\) but \(n=(k T_{o}) / T\). Thus,
$$\Omega=\frac{2 \pi}{N}=\frac{2 \pi T}{k T_{o}}=\frac{1}{k} \omega_{o} T=\frac{q}{LCM(p, q)} \omega_{o} T$$

(c) We need to find a value of \(m\) such that \(x[n+N]=x(n T+m T_{o})\). Therefore, \(N=m(T_{o} / T)\), where \(m(T_{o} / T)\) must be an integer, or \(m(q / p)\) must be an integer. Thus, \(m q=LCM(p, q)\), \(m=LCM(p, q) / q\)

---

MIT OpenCourseWare
[http://ocw.mit.edu](http://ocw.mit.edu)
Resource: Signals and Systems
Professor Alan V. Oppenheim

The following may not correspond to a particular course on MIT OpenCourseWare, but has been provided by the author as an individual learning resource.

For information about citing these materials or our Terms of Use, visit: [http://ocw.mit.edu/terms](http://ocw.mit.edu/terms)
