# SofinLoop.py
import mmap
import os
import struct
import time

class CoSimInterface:
    def __init__(self, use_dummy=False, filename="ControlDirect_SharedMemory"):
        self.use_dummy = use_dummy
        self.filename = filename
        
        # 状态机标志位偏移量
        self.OFFSET_STARCCM = 0
        self.OFFSET_TETHRA  = 4
        self.OFFSET_ROVCTRL = 8
        
        # 数据区偏移量 (严格按照 C++ 结构体的字节计算)
        self.READ_OFFSET_STATE = 16   # 13个 double (时间、位置、姿态、速度、角速度) 的起始位置
        self.WRITE_OFFSET_RPM = 120   # 6个 double (推进器转速) 的起始位置
        
        self.mm = None
        
        if not self.use_dummy:
            print(f"正在连接三方耦合共享内存文件: {self.filename}")
            try:
                fd = os.open(self.filename, os.O_RDWR)
                # 总大小为 1032 字节保持不变
                self.mm = mmap.mmap(fd, 1032, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)
            except FileNotFoundError:
                raise FileNotFoundError(f"Cannot found {self.filename}...")
        else:
            # 测试模式变量
            self.sim_time = 0.0
            self.dt = 0.001
            self.dummy_state = {
                'timestamp': 0.0, 'x': 0.0, 'y': 0.0, 'z': -5.0,
                'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0,
                'u': 0.35, 'v': 0.0, 'w': 0.0,
                'p': 0.0, 'q': 0.0, 'r': 0.0
            }

    def wait_for_cfd_data(self):
        """阻塞等待 FLAG_ROVCTRL 置 1 (接下 Tethra 的接力棒)"""
        if self.use_dummy:
            self.sim_time += self.dt
            self.dummy_state['timestamp'] = self.sim_time
            self.dummy_state['x'] += self.dummy_state['u'] * self.dt
            time.sleep(0.0001)
            return self.dummy_state.copy()
            
        while True:
            # 读取 ROVCTRL 的轮询标志位
            self.mm.seek(self.OFFSET_ROVCTRL)
            rovctrl_turn = struct.unpack('i', self.mm.read(4))[0]
            
            if rovctrl_turn == 1:
                # 轮到控制模块计算，从偏移量 16 开始读取 13 个 double 数据 (104字节)
                self.mm.seek(self.READ_OFFSET_STATE)
                raw_data = self.mm.read(104) 
                unpacked = struct.unpack('13d', raw_data)
                
                state = {
                    'timestamp': unpacked[0],
                    'x': unpacked[1], 'y': unpacked[2], 'z': unpacked[3],
                    'roll': unpacked[4], 'pitch': unpacked[5], 'yaw': unpacked[6],
                    'u': unpacked[7], 'v': unpacked[8], 'w': unpacked[9],
                    'p': unpacked[10], 'q': unpacked[11], 'r': unpacked[12]
                }
                return state
                
            # 休眠极短时间，降低 CPU 轮询消耗
            time.sleep(0.001)

    def send_motor_commands(self, rpm_array):
        """将推力器转速写入内存，并将控制权闭环交回给 STAR-CCM+"""
        if self.use_dummy:
            return
            
        # 1. 打包 6 个转速数据 (6 * 8 = 48 字节)
        rpm_bytes = struct.pack('6d', *rpm_array)
        
        # 2. 写入指定的转速偏移位置 (120)
        self.mm.seek(self.WRITE_OFFSET_RPM)
        self.mm.write(rpm_bytes)
        
        # 3. 翻转标志位：ROVCTRL 置 0，唤醒 STARCCM (闭环)
        self.mm.seek(self.OFFSET_ROVCTRL)
        self.mm.write(struct.pack('i', 0))
        
        self.mm.seek(self.OFFSET_STARCCM)
        self.mm.write(struct.pack('i', 1))

    def close(self):
        if self.mm is not None:
            self.mm.close()
