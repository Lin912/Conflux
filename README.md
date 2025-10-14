# The Conflux
An open source code for simulate the dynamic characteric of tethered Rigids.

## PART 1 <Tethra(Nowdays Released Version->5.2)>
For Linux Server paltfoam we release the ***Tethra 5.2*** which used for simulate the dynamic behaivor of **Cable** & **Underwater chians** & **Marine risers**.

The Porocess Folder include the Jacabian Matrix proceducer, Newton itterator, Data processor and, a Plotting part. 

### 1.1 Theory





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
