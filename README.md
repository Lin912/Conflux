# The Conflux
An open source code for simulate the dynamic characteric of tethered Rigids.


## PART 1 Theory

### 1.1 Coordinate system definition and model construction
Three different coordinate systems are used in the derivation to the mathematical model of the underwater tethered system, i.e. the fixed inertial coordinate system $(X,Y,Z)$, the local coordinate systems for cable elements $(t,n,b)$ and the local system for tethered vehicle $(X_{r},Y_{r},Z_{r})$

A module dealing with numerical solution of established mathematical model for cable and a CFD module dealing with determination of the hydrodynamic characteristics of tethered vehicle are first constructed, the two modules are then interfaced dynamically at the conjunction point between the lower end of the cable and the towed point of tethered vehicle. By this way, the numerical model of the underwater tethered system is constructed. 
	
In the numerical simulation process, the velocity components at the upper end of the cable, which is connected with a working ship on water surface, serve as an active motivation to control the underwater tethered system.

### 1.2 Coordinate transformation

The local coordinate systems for cable elements $(t,n,b)$ are orthogonal coordinates that are specific to each point of the cable elements. The local frame's orientation is selected such that $t$ represents the tangent to cable element in the direction of increasing unstretched cable element length, $n$ represents the normal direction, and $b$ completes a right-handed coordinate system. The fixed inertial coordinate system $(X,Y,Z)$ remains fixed in space, with $Y$ and $Z$ being in the horizontal plane and $X$ directed downwards. Assuming that the torsion effect of the cable is ignored, the relationship between the two frames $(X,Y,Z)$ and $(t,n,b)$ at any location of a cable element is:

$$
    (t,n,b) = (X,Y,Z)[T]
$$

where,

$$
		[T] = 
		\begin{bmatrix}
			cos\phi cos\theta&	-sin\phi&	cos\phi sin\theta\\
			cos\theta sin\phi&	cos\phi &	sin\phi sin\theta\\
			-sin\theta&			0&			cos\theta\\
		\end{bmatrix}
$$

with the symbol $\phi$ denotes the rotation Euler angle around $Z$-axis, while $\theta$ specifies the rotation Euler angle around $Y$-axis.

### 1.3 Governing equations for cable element
The cable in the system is considered to be a lengthy, slender, flexible circular cylinder that exhibits significant geometric and material nonlinearity in its dynamic behavior. In establishing the model, following assumptions are made:
\begin{enumerate}
		\item The cross-section of cable element is homogeneous, with a regular circular shape.
		\item The effect of bending moment of cable element is represented by the Euler-Bernoulli beam theory.
		\item The tension and deflection of cable element satisfy the Hooke's law.
\end{enumerate}

Under these assumptions, the following relationships can be found:
	
$$
		{d_p} = (1+e) {d_s}
$$
	
$$
		e = \frac{T}{EA}
		\label{Eq4}
$$

where $d_s$ and $d_p$ represent the lengths of the cable element before and after being stretched, and $e$ denotes the magnitude of the axial strain. $T$ represents the tension which is a component of the internal force acting on the cable element. While, the symbol $A$ denotes the cross-section area of cable. $E$ is the Young's modulus of cable.
	
Considering a unit length of a stretched cable element located at the local coordinate systems$(t,n,b)$, the cable element conforms to the law of conservation of mass. The balance of forces at any location of cable element can be written as:

$$
	m\frac{D\vec{V}}{Dt} = \frac{D\vec{N}}{Ds} + (1+e)\sum \vec{R}
	\label{Eq5}
$$

or

$$
	m\frac{D\vec{V}}{Dt} = \frac{D\vec{N}}{Ds} + (1+e)(\vec{R_g} + \vec{R_i} + \vec{R_r})
	\label{Eq6}
$$

In Equation \eqref{Eq6}, $\vec{V}$ and $\vec{N}$ denote the velocity and internal force vectors of a cable element. The velocity vector can be expressed in component form as $\vec{V}=(u,v,w)$. The internal force vector $\vec{N}$ can be expressed as $\vec{N}=(T,S_n,S_b)$. The symbols $\vec{R_g}$, $\vec{R_i}$, and $\vec{R_r}$ on the right side of the equation denote the submerged weight, the inertial force, and the damping forces on the cable element respectively. The combined force $\sum \vec{R}$ represents the external effect that indicates the influence of fluid and gravity on the cable element. Therefore, the external forces can be expressed as follows:
	
$$
	(1+e)\vec{R_g} = (-w) sin\phi cos\theta \vec{t} + (-w)cos\phi \vec{n} + (-w)sin\phi sin\theta \vec{b}
	\label{Eq7}
$$ 
	
$$
	(1+e)\vec{R_i} = -m_a \frac{\partial v}{\partial t} \vec{n} - m_a \frac{\partial w}{\partial t} \vec{b}
	\label{Eq8}
$$
	
$$
	(1+e)\vec{R_r} = R_r{}_t \vec{t} + R_r{}_n \vec{n} + R_r{}_b \vec{b}
	\label{Eq9}
$$

where, $m_a$ represents the additional mass, and $w$ the submerged weight. The damping force is determined by the Morison equation:

$$
	R_r{}_t = -\frac{1}{2} \pi \rho d C_d{}_t u |u| \sqrt{1+e}
	\label{Eq10}
$$
	
$$
	R_r{}_n = -\frac{1}{2} \rho d C_d{}_n v \sqrt{v^2 + w^2} \sqrt{1+e}
	\label{Eq11}
$$
	
$$
	R_r{}_b = -\frac{1}{2} \rho d C_d{}_b w \sqrt{v^2 + w^2} \sqrt{1+e}
	\label{Eq12}
$$

In Equations \eqref{Eq10} to \eqref{Eq12}, $\rho$ represents the density of water, $d$ refers to the diameter of the cable element’s cross-sectional area. $C_{dt}$, $C_{dn}$, and $C_{db}$ are the Morison coefficient indicates the force of fluid acting on the cable element.$C_{dt}$ is the inertia coefficient while $C_{dn}$, and $C_{db}$ are the drag coefficient. 
	
Equation \eqref{Eq5} can be written as a system of three scalar equations by taking components in three independent directions. Components in directions $(t,n,b)$ give:
	
$$
	m \frac{\partial u}{\partial t} + m(\omega_2 w - \omega_3 v) - \frac{\partial T}{\partial s} - (S_b \Omega_2 - S_n \Omega_3) - (w_{}sin\phi cos\theta +\frac{1}{2} \pi \rho d_0 C_d{}_t u |u| \sqrt{1+e}) = 0
	\label{Eq13}
$$
	
$$
	m \frac{\partial v}{\partial t} + m(\omega_3 u - \omega_1 w) - \frac{\partial S_n}{\partial s} - (T \Omega_3 - S_b \Omega_1) - (w_{}cos \phi +m_a \frac{\partial v}{\partial t} +\frac{1}{2} \rho d_0 C_d{}_n v \sqrt{v^2 +w^2} \sqrt{1+e}) = 0
	\label{Eq14}
$$
	
$$
	m \frac{\partial w}{\partial t} + m(\omega_1 v - \omega_2 u) - \frac{\partial S_b}{\partial s} - (S_n \Omega_1 - T \Omega_2) - (w_{}sin \phi sin \theta +m_a \frac{\partial w}{\partial t} +\frac{1}{2} \rho d_0 C_d{}_b w \sqrt{v^2 + w^2} \sqrt{1+e}) = 0
	\label{Eq15}
$$

where the variables $\omega_1$, $\omega_2$, and $\omega_3$ represent the components of angular velocity around the $t$, $n$, and $b$ axes, respectively. The components $\Omega_1$, $\Omega_2$, and $\Omega_3$ represent the Darboux vector $\vec{\Omega}$, which describes the space curvature of the cable element along the $(t,n,b)$ axis.
	
The conservation of momentum equation is adopted to describe the effects of bending moment on the cable element. The bending effect can prevent the divergence of the solution process because the Euler angle matrix becomes singular when the bending moment effects are neglected. The conservation of momentum equation referenced the solution process of the internal flow effect on vibrating catenary risers, as discussed by \cite{RN1658}:
	
$$
	\frac{1}{1+e}\frac{D[\rho_c I \vec{\omega}]}{Dt} = \frac{1}{(1+e)^2}(\frac{\partial \vec{M}}{\partial s}+\vec{\Omega} \times \vec{M})+\vec{t} \times (1+e)\vec{N}
	\label{Eq16}
$$

where $\vec{M}$ is the sum of the bending moment components in $\vec{n}$ and $\vec{b}$ direction, with the relation $\vec{M} = M_n \vec{n} + M_b \vec{b}$. And the detailed description of the two components are $M_n = E I \Omega_2$ and $M_b = E I \Omega_3$.
	
Expanding the Equation \eqref{Eq16} in two directions, with neglecting the torsion effect, the equations can be written as:
	
$$
	(1+e)\rho_c I \frac{\partial \omega_2}{\partial t} - E I \frac{\partial \Omega_2}{\partial s} +  E I \Omega_1 \Omega_3 + S_b (1+e)^3 = 0
	\label{Eq17}
$$
	
$$
	(1+e)\rho_c I \frac{\partial \omega_3}{\partial t} - E I \frac{\partial \Omega_3}{\partial s} + E I \Omega_1 \Omega_2 + S_n (1+e)^3 = 0
	\label{Eq18}
$$
	
To ensure the continuity of the selected cable element with the adjacent elements, it is necessary to give the compatibility relation equations for the element. The position vector $\vec{S}(s,t)$ should satisfy smoothness conditions in both the $t$ and $s$ spaces. Then, the equations for the compatibility relation are derived: 
	
$$
	\frac{D}{D t}[(1+e)\vec{S}] = \frac{D \vec{V}}{D s}
	\label{Eq19}
$$

with $e$ can be expressed as $T/EA$ aforementioned, the Equation(19) can be expanded as:

$$
	\frac{1}{EA} \frac{\partial T}{\partial t} - \frac{\partial u}{\partial s} - (\Omega_2 w - \Omega_3 v) = 0
	\label{Eq20}
$$
	
$$
	(1+e)\omega_3 - \frac{\partial v}{\partial s} - (\Omega_3 u - \Omega_1 w) = 0
	\label{Eq21}
$$
	
$$
	(1+e)\omega_2 + \frac{\partial w}{\partial s} + (\Omega_1 v - \Omega_2 u) = 0
	\label{Eq22}
$$
	
There are $11$ unknown variables in Equations \eqref{Eq13} to \eqref{Eq15}, \eqref{Eq17} to \eqref{Eq18}, and \eqref{Eq20} to \eqref{Eq22}, that is,

\begin{itemize}
	\item the three components of velocity $\vec{V} = (u,v,w)$ of cable element in local coordinate system $(t,n,b)$;
	\item the three component of internal force $\vec{N} = (T, S_n, S_b)$ of cable element;
	\item the Euler angle $\theta$ and $\phi$ which describe the orientation of the rotation around the normal and bi-normal direction;
	\item the three component of Darboux vector $\vec{\Omega} = (\Omega_1, \Omega_2, \Omega_3)$ of cable element which represent the space curvature of $(t,n,b)$ axes.
\end{itemize}
	
In order to obtain a solvable system, three more equations are required.  These equations are provided by the Euler angular velocity derivation procedure: 
	 
$$
	\Omega_1 = -\sin\theta \frac{d\phi}{ds}
	\label{Eq23}
$$
	
$$
	\Omega_2 = \frac{d\theta}{ds}
	\label{Eq24}
$$
	
$$
	\Omega_3 = \cos\theta \frac{d\phi}{ds}
	\label{Eq25}
$$

In the Equation \eqref{Eq23} and \eqref{Eq25}, the right-hand component have a relation of multiples. It can be seen that the relation between  $\Omega_1$ and $\Omega_3$ is
	
$$
	\Omega_1 = -tan \theta \Omega_3
	\label{Eq26}
$$
	
To simplify the calculation process, the unknown variable $\Omega_1$ is represented by the product of variables $\Omega_3$ and $tan \theta$. Then, the quantity of unknown variables is reduced to $10$. Equations \eqref{Eq24} and \eqref{Eq25} and Equations \eqref{Eq13} to \eqref{Eq15}, \eqref{Eq17} to \eqref{Eq18}, and \eqref{Eq20} to \eqref{Eq22} form a complete set of equations of motion for the cable element. The ten equations can be written in a matrix form as:
	
$$
	M \frac{\partial \vec{Y}}{\partial t} + N \frac{\partial \vec{Y}}{\partial s} + Q = 0
	\label{Eq27}
$$

where $\vec{Y} = [u, v, w, T, S_n, S_b, \theta, \phi, \Omega_n, \Omega_b]^T$ is variables vector.
	









## PART 2 <Tethra(Nowdays Released Version->5.2)>
For Linux Server paltfoam we release the ***Tethra 5.2*** which used for simulate the dynamic behaivor of **Cable** & **Underwater chians** & **Marine risers**.

The Porocess Folder include the Jacabian Matrix proceducer, Newton itterator, Data processor and, a Plotting part. 




### 2.2 Usage process
The code is written by the C++, before download the code you parper:

1.A compilable Cpp environment, download the GNU complier;

2.Download and install the Eigen library;

3.Install Cmake and compile the source files according to CmakeLists.


Then enjoy the complex dynamic process of Cable-Rigid system by->

Running the Tethra.exe and view the calculations result in the csv folder. The output.csv is the result file.
Then viewing the graphical results with using the code in Python folder, the PostProcess folder includes the Force and Profile result.

Notes:
Specify the CMake source path and the CMake executable path.

### 2.3 Cases of solution


## PART 3 <HydroSimulation>

### 3.1 Macro for Case

### 3.2 Usage process

Download the StarCCM+, a commerical CFD code, and buy the Server License.


### 3.3 Some infos




## PART 4 <Data interaction>

### 4.1 Memory mapped file(MMF)

**What is that?**

**->** The Memory-Mapped File (MMF) is an OS mechanism that maps a file directly into a process's virtual address space. This allows an application to access file data as if it were resident in memory, using direct pointer operations rather than traditional read/write calls.

**How does it works?** 

**->** The operating system establishes a correlation between the file on disk and a range of virtual memory addresses. When the program accesses a memory address within this range, the OS transparently loads the corresponding file data from disk into physical RAM (via a page fault). This provides a seamless, on-demand loading mechanism.

**Why we choose that?** 

**->** High-Performance File I/O, Inter-Process Communication(IPC) ,and Handling Large Files Efficiently.

### 4.2 Active Polling process
**What is that?** 

**->** Active Polling is a synchronous programming pattern where a client process repeatedly and proactively checks the status of a server, device, or resource to see if it has new data, is ready for a transaction, or has changed state. It is a "pull" model. The client does not wait for a notification; instead, it takes the initiative to ask, "*Are you ready yet?* :)" at regular intervals. The key characteristic is that the client is always in control and expends its own computational effort to perform these checks, regardless of whether there is new information or not.

**Why we choose that?** 

**->** Simplicity and Predictability: The logic is linear, making the code easy to write, understand, and debug. There is no complex setup for event handlers or callback functions. Avoids Complex Asynchronous Code: It avoids the potential complexity of asynchronous programming paradigms, which can sometimes lead to convoluted code known as "*callback hell.*"

### 4.3 About Data info



## PART 5 <Expermental verrication>

### 5.1 The Experments process


### 5.2 Simulation parameters

### 5.3 Data comparison


## Contact Me
Auther's Information:

Email: T.Zhang@outlook.com

github :[lin912] (https://github.com/Lin912)

ORCid (0009-0008-3501-429X)
