# 2 Signals and Systems: Part I
In this lecture, we consider a number of basic signals that will be important building blocks later in the course. Specifically, we discuss both continuous-time and discrete-time sinusoidal signals as well as real and complex exponentials.

Sinusoidal signals for both continuous time and discrete time will become important building blocks for more general signals, and the representation using sinusoidal signals will lead to a very powerful set of ideas for representing signals and for analyzing an important class of systems. We consider a number of distinctions between continuous-time and discrete-time sinusoidal signals. For example, continuous-time sinusoids are always periodic. Furthermore, a time shift corresponds to a phase change and vice versa. Finally, if we consider the family of continuous-time sinusoids of the form \(A \cos \omega_{0} t\) for different values of \(\omega_{0}\), the corresponding signals are distinct. The situation is considerably different for discrete-time sinusoids. Not all discrete-time sinusoids are periodic. Furthermore, while a time shift can be related to a change in phase, changing the phase cannot necessarily be associated with a simple time shift for discrete-time sinusoids. Finally, as the parameter \(\Omega_{0}\) is varied in the discrete-time sinusoidal sequence \(A \cos (\Omega_{0} n+\phi)\) two sequences for which the frequency \(\Omega_{0}\) differs by an integer multiple of \(2 \pi\) are in fact indistinguishable.

Another important class of signals is exponential signals. In continuous time, real exponentials are typically expressed in the form \(c e^{a t}\) whereas in discrete time they are typically expressed in the form \(c \alpha^{n}\)

A third important class of signals discussed in this lecture is continuous-time and discrete-time complex exponentials. In both cases the complex exponential can be expressed through Euler's relation in the form of a real and an imaginary part, both of which are sinusoidal with a phase difference of \(\pi / 2\) and with an envelope that is a real exponential. When the magnitude of the complex exponential is a constant, then the real and imaginary parts neither grow nor decay with time; in other words, they are purely sinusoidal. In this case for continuous time, the complex exponential is periodic. For discrete time the complex exponential may or may not be periodic depending on whether the sinusoidal real and imaginary components are periodic.

In addition to the basic signals discussed in this lecture, a number of additional signals play an important role as building blocks. These are introduced in Lecture 3.

## Suggested Reading
- Section 2.2, Transformations of the Independent Variable, pages 12-16
- Section 2.3.1, Continuous-Time Complex Exponential and Sinusoidal Signals, pages 17-22
- Section 2.4.2, Discrete-Time Complex Exponential and Sinusoidal Signals, pages 27-31
- Section 2.4.3, Periodicity Properties of Discrete-Time Complex Exponentials, pages 31-35

## Continuous-Time Sinusoidal Signal
### Ideal Signal Expression
$$x(t)=A \cos \left(\omega_{0} t+\phi\right)$$

### TRANSPARENCY 2.1
Continuous-time sinusoidal signal indicating the definition of amplitude, frequency, and phase.
- **Periodic Property**
  $$x(t)=x\left(t+T_{0}\right)$$
  Period \(\triangleq\) smallest \(T_{0}\)
  $$A \cos \left[\omega_{0} t+\phi\right]=A \cos \left[\omega_{0} t+\omega_{0} T_{0}+\phi\right]$$
  The equation holds when \(\omega_{0} T_{0}=2 \pi m\) (\(m\) is integer), so the fundamental period is
  $$T_{0}=\frac{2 \pi}{\omega_{0}}$$

### TRANSPARENCY 2.2
Relationship between a time shift and a change in phase for a continuous-time sinusoidal signal.
- **Time Shift \(\Leftrightarrow\) Phase Change**
  $$A \cos \left[\omega_{0}\left(t+t_{0}\right)\right]=A \cos \left[\omega_{0} t+\omega_{0} t_{0}\right]$$
  $$A \cos \left[\omega_{0}\left(t+t_{0}\right)+\phi\right]=A \cos \left[\omega_{0} t+\omega_{0} t_{0}+\phi\right]$$

### TRANSPARENCY 2.3
Illustration of the signal \(A \cos \omega_{0} t\) as an even signal.
- When \(\phi=0\), the signal is
  $$x(t)=A \cos \omega_{0} t$$
- **Even Signal Property**: \(x(t)=x(-t)\)
- **Periodic Property**: \(x(t)=x\left(t+T_{0}\right)\)

### TRANSPARENCY 2.4
Illustration of the signal \(A \sin \omega_{0} t\) as an odd signal.
- When \(\phi=-\frac{\pi}{2}\), the signal can be written as
  $$x(t)=\left\{\begin{array}{l}A \cos \left(\omega_{0} t-\frac{\pi}{2}\right) \\ A \sin \omega_{0} t \\ A \cos \left[\omega_{0}\left(t-\frac{T_{0}}{4}\right)\right] \end{array}\right.$$
- **Odd Signal Property**: \(x(t)=-x(-t)\)
- **Periodic Property**: \(x(t)=x\left(t+T_{0}\right)\)

## Discrete-Time Sinusoidal Signal
### Ideal Signal Expression
$$x[n]=A \cos \left(\Omega_{0} n+\phi\right)$$

### TRANSPARENCY 2.5
Illustration of discrete-time sinusoidal signals.

### TRANSPARENCY 2.6
Relationship between a time shift and a phase change for discrete-time sinusoidal signals. In discrete time, a time shift always implies a phase change.
- **Time Shift \(\Rightarrow\) Phase Change**
  $$A \cos \left[\Omega_{0}\left(n+n_{0}\right)\right]=A \cos \left[\Omega_{0} n+\Omega_{0} n_{0}\right]$$

### TRANSPARENCY 2.7
The sequence \(A \cos \Omega_{0} n\) illustrating the symmetry of an even sequence.
- When \(\phi=0\), the sequence is
  $$x[n]=A \cos \Omega_{0} n$$
- **Even Sequence Property**: \(x[n]=x[-n]\)

### TRANSPARENCY 2.8
The sequence \(A \sin \Omega_{0} n\) illustrating the antisymmetric property of an odd sequence.
- When \(\phi=-\frac{\pi}{2}\), the sequence can be written as
  $$x[n]=\left\{\begin{array}{l} A \cos \left(\Omega_{0} n-\frac{\pi}{2}\right) \\ A \sin \Omega_{0} n \\ A \cos \left[\Omega_{0}\left(n-n_{0}\right)\right] \end{array}\right.$$
- Given \(\Omega_{0}=\frac{\pi}{8}\), solve for \(n_0\)
- **Odd Sequence Property**: \(x[n]=-x[-n]\)

### TRANSPARENCY 2.9
For a discrete-time sinusoidal sequence a time shift always implies a change in phase, but a change in phase might not imply a time shift.
- Time shift leads to phase change
  $$A \cos \left[\Omega_{0}\left(n+n_{0}\right)\right]=A \cos \left[\Omega_{0} n+\Omega_{0} n_{0}\right]$$
- Phase change does not necessarily correspond to time shift
  $$A \cos \left[\Omega_{0}\left(n+n_{0}\right)\right] \stackrel{?}{=} A \cos \left[\Omega_{0} n+\phi\right]$$

### TRANSPARENCY 2.10
The requirement on \(\Omega_{0}\) for a discrete-time sinusoidal signal to be periodic.
- **Periodicity Condition**: \(x[n]=x[n+N]\) (smallest integer \(N\) is the period)
  $$A \cos \left[\Omega_{0}(n+N)+\phi\right]=A cos [\Omega_{0} n+\Omega_{0} N+\phi]$$
- The equation holds when \(\Omega_{0} N=2 \pi m\) (\(m\) is integer)
  $$N=\frac{2 \pi m}{\Omega_{0}}$$
- \(N\) and \(m\) must both be integers, otherwise the sequence is non-periodic

### TRANSPARENCY 2.11
Several sinusoidal sequences illustrating the issue of periodicity.

### TRANSPARENCY 2.12
Some important distinctions between continuous-time and discrete-time sinusoidal signals.
| Continuous-Time Sinusoid \(A \cos \left(\omega_{0} t+\phi\right)\) | Discrete-Time Sinusoid \(A \cos \left(\Omega_{0} n+\phi\right)\) |
| ---- | ---- |
| Distinct signals for distinct values of \(\omega_{0}\) | Identical signals for values of \(\Omega_{0}\) separated by \(2 \pi\) |
| Periodic for any choice of \(\omega_{0}\) | Periodic only if \(\Omega_{0}=\frac{2 \pi m}{N}\) for some integers \(N>0\) and \(m\) |

## Sinusoidal Signals at Distinct Frequencies
### Continuous Time
$$x_{1}(t)=A \cos \left(\omega_{1} t+\phi\right)$$
$$x_{2}(t)=A \cos \left(\omega_{2} t+\phi\right)$$
If \(\omega_{2} \neq \omega_{1}\), then \(x_{2}(t) \neq x_{1}(t)\)

### Discrete Time
$$x_{1}[n]=A \cos \left[\Omega_{1} n+\phi\right]$$
$$x_{2}[n]=A \cos \left[\Omega_{2} n+\phi\right]$$
If \(\Omega_{2}=\Omega_{1}+2 \pi m\), then \(x_{2}[n]=x_{1}[n]\)

### TRANSPARENCY 2.13
Continuous-time sinusoidal signals are distinct at distinct frequencies. Discrete-time sinusoidal signals are distinct only over a frequency range of \(2 \pi\)

## Real Exponential Signal
### Continuous-Time Real Exponential
- **Expression**: \(x(t)=Ce^{at}\)
  - \(C\) and \(a\) are real numbers
  - When \(a>0\), the signal grows exponentially with time
  - When \(a<0\), the signal decays exponentially with time
- **Time Shift \(\Leftrightarrow\) Scale Change**
  $$Ce^{a\left(t+t_{0}\right)}=Ce^{a t_{0}} e^{at }$$
- **TRANSPARENCY 2.14**: Illustration of continuous-time real exponential signals

### Discrete-Time Real Exponential
- **Expression**: \(x[n]=C e^{\beta n}=C \alpha^{n}\)
  - \(C\) and \(\alpha\) are real numbers
  - When \(|\alpha|>1\), the sequence grows with \(n\)
  - When \(|\alpha|<1\), the sequence decays with \(n\)
- **TRANSPARENCY 2.15**: Illustration of discrete-time real exponential sequences

## Complex Exponential Signal
### Continuous-Time Complex Exponential
- **Expression**: \(x(t)=Ce^{at}\)
  - \(C\) and \(a\) are complex numbers
  - Let \(C=|C| e^{j \theta}\), \(a=r+j \omega_{0}\), then
  $$
  \begin{aligned} x(t) & =|C| e^{j \theta} e^{\left(r+j \omega_{0}\right) t} \\ & =|C| e^{r t} e^{j\left(\omega_{0} t+\theta\right)} \end{aligned}
  $$
- **Euler's Relation Application**
  $$x(t)=|C| e^{r t} cos \left(\omega_{0} t+\theta\right)+j|C| e^{r t} sin \left(\omega_{0} t+\theta\right)$$
- **TRANSPARENCY 2.16**: Continuous-time complex exponential signals and their relationship to sinusoidal signals
- **TRANSPARENCY 2.17**: Sinusoidal signals with exponentially growing (\(r>0\)) and exponentially decaying (\(r<0\)) envelopes

### Discrete-Time Complex Exponential
- **Expression**: \(x[n]=C \alpha^{n}\)
  - \(C\) and \(\alpha\) are complex numbers
  - Let \(C=|C| e^{j \theta}\), \(\alpha=|\alpha| e^{j \Omega_{0}}\), then
  $$
  \begin{aligned} x[n] & =|C| e^{j \theta}\left(|\alpha| e^{j \Omega_{0}}\right)^{n} \\ & =|C||\alpha|^{n} e^{j\left(\Omega_{0} n+\theta\right)} \end{aligned}
  $$
- **Euler's Relation Application**
  $$x[n]=|C||\alpha|^{n} cos \left(\Omega_{0} n+\theta\right)+j|C||\alpha|^{n} sin \left(\Omega_{0} n+\theta\right)$$
- When \(|\alpha|=1\), the real and imaginary parts are pure sinusoidal sequences
- **Periodicity**: \(Ce^{j \Omega_{o} n}\) is periodic if and only if \(\Omega_0\) meets the discrete-time sinusoid periodicity condition
- **TRANSPARENCY 2.18**: Discrete-time complex exponential signals and their relationship to sinusoidal signals
- **TRANSPARENCY 2.19**: Sinusoidal sequences with geometrically growing (\(|\alpha|>1\)) and geometrically decaying (\(|\alpha|<1\)) envelopes

---
MIT OpenCourseWare
[http://ocw.mit.edu](http://ocw.mit.edu)
Resource: Signals and Systems
Professor Alan V. Oppenheim

The following may not correspond to a particular course on MIT OpenCourseWare, but has been provided by the author as an individual learning resource.

For information about citing these materials or our Terms of Use, visit: [http://ocw.mit.edu/terms](http://ocw.mit.edu/terms)
