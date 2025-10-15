# The Conflux
An open source code for simulate the dynamic characteric of tethered Rigids.

## PART 1 <Tethra(Nowdays Released Version->5.2)>
For Linux Server paltfoam we release the ***Tethra 5.2*** which used for simulate the dynamic behaivor of **Cable** & **Underwater chians** & **Marine risers**.

The Porocess Folder include the Jacabian Matrix proceducer, Newton itterator, Data processor and, a Plotting part. 

### 1.1 Theory

#### Coordinate system definition and model construction
Three different coordinate systems are used in the derivation to the mathematical model of the underwater tethered system, i.e. the fixed inertial coordinate system $(X,Y,Z)$, the local coordinate systems for cable elements $(t,n,b)$ and the local system for tethered vehicle $(X_{r},Y_{r},Z_{r})$

a module dealing with numerical solution of established mathematical model for cable and a CFD module dealing with determination of the hydrodynamic characteristics of tethered vehicle are first constructed, the two modules are then interfaced dynamically at the conjunction point between the lower end of the cable and the towed point of tethered vehicle. By this way, the numerical model of the underwater tethered system is constructed. 
	
In the numerical simulation process, the velocity components at the upper end of the cable, which is connected with a working ship on water surface, serve as an active motivation to control the underwater tethered system.

#### Coordinate transformation

The local coordinate systems for cable elements $(t,n,b)$ are orthogonal coordinates that are specific to each point of the cable elements. The local frame's orientation is selected such that $t$ represents the tangent to cable element in the direction of increasing unstretched cable element length, $n$ represents the normal direction, and $b$ completes a right-handed coordinate system. The fixed inertial coordinate system $(X,Y,Z)$ remains fixed in space, with $Y$ and $Z$ being in the horizontal plane and $X$ directed downwards. Assuming that the torsion effect of the cable is ignored, the relationship between the two frames $(X,Y,Z)$ and $(t,n,b)$ at any location of a cable element is:

\begin{equation}
		(t,n,b) = (X,Y,Z)[T]
		\label{Eq1}
	\end{equation}
	where
	\begin{equation}
		[T] = 
		\begin{bmatrix}
			cos\phi cos\theta&	-sin\phi&	cos\phi sin\theta\\
			cos\theta sin\phi&	cos\phi &	sin\phi sin\theta\\
			-sin\theta&			0&			cos\theta\\
		\end{bmatrix}
	\label{Eq2}
\end{equation}

with the symbol $\phi$ denotes the rotation Euler angle around $Z$-axis, while $\theta$ specifies the rotation Euler angle around $Y$-axis.













### 1.2 Usage process
The code is written by the C++, before download the code you parper:

1.A compilable Cpp environment, download the GNU complier;

2.Download and install the Eigen library;

3.Install Cmake and compile the source files according to CmakeLists.


Then enjoy the complex dynamic process of Cable-Rigid system by->

Running the Tethra.exe and view the calculations result in the csv folder. The output.csv is the result file.
Then viewing the graphical results with using the code in Python folder, the PostProcess folder includes the Force and Profile result.

Notes:
Specify the CMake source path and the CMake executable path.

### 1.3 Cases of solution


## PART 2 <HydroSimulation>

### 2.1 Macro for Case

### Usage process

Download the StarCCM+, a commerical CFD code, and buy the Server License.


### Some infos




## PART 3 <Data interaction>

### 3.1 Memory mapped file(MMF)

**What is that?**

**->** The Memory-Mapped File (MMF) is an OS mechanism that maps a file directly into a process's virtual address space. This allows an application to access file data as if it were resident in memory, using direct pointer operations rather than traditional read/write calls.

**How does it works?** 

**->** The operating system establishes a correlation between the file on disk and a range of virtual memory addresses. When the program accesses a memory address within this range, the OS transparently loads the corresponding file data from disk into physical RAM (via a page fault). This provides a seamless, on-demand loading mechanism.

**Why we choose that?** 

**->** High-Performance File I/O, Inter-Process Communication(IPC) ,and Handling Large Files Efficiently.

### 3.2 Active Polling process
**What is that?** 

**->** Active Polling is a synchronous programming pattern where a client process repeatedly and proactively checks the status of a server, device, or resource to see if it has new data, is ready for a transaction, or has changed state. It is a "pull" model. The client does not wait for a notification; instead, it takes the initiative to ask, "*Are you ready yet?* :)" at regular intervals. The key characteristic is that the client is always in control and expends its own computational effort to perform these checks, regardless of whether there is new information or not.

**Why we choose that?** 

**->** Simplicity and Predictability: The logic is linear, making the code easy to write, understand, and debug. There is no complex setup for event handlers or callback functions. Avoids Complex Asynchronous Code: It avoids the potential complexity of asynchronous programming paradigms, which can sometimes lead to convoluted code known as "*callback hell.*"

### 3.3 About Data info



## PART 4 <Expermental verrication>

### The Experments process


### Simulation parameters

### Data comparison

## Contact Me
Auther's Information:

Email: T.Zhang@outlook.com

github :[lin912] (https://github.com/Lin912)

ORCid (0009-0008-3501-429X)
