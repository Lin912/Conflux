import star.common.*;
import java.io.*;
import java.util.*;
import star.base.neo.*;
import star.sixdof.*;
import star.base.report.*;

import java.io.RandomAccessFile;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.ByteOrder;

public class FileConditioned extends StarMacro {
    private static final String FILE_SHARED = "../HydroSimulation/ControlDirect_SharedMemory";
    
    private static final int OFFSET_FLAG_STARCCM = 0;
    private static final int OFFSET_FLAG_TETHRA  = 4;
    private static final int OFFSET_FLAG_ROVCTRL = 8;

    private static final int BUFFER_SIZE = 1032;        // 总大小 1032 字节
    private static final int OFFSET_DATA_START = 16;    // 13 个状态量 (时间戳、位置、姿态、线速度、角速度) 起始点
    private static final int OFFSET_RPM_IN = 120;       // 6 个螺旋桨转速起始点
    private static final int OFFSET_FORCE_IN = 168;     // 3 个绳缆力 (X, Y, Z) 起始点

    @Override
    public void execute() {
        try {
            Simulation simulation = getActiveSimulation();
            
            RandomAccessFile file = new RandomAccessFile(FILE_SHARED, "rw");
            FileChannel channel = file.getChannel();
            MappedByteBuffer buffer = channel.map(FileChannel.MapMode.READ_WRITE, 0, BUFFER_SIZE);
            buffer.order(ByteOrder.LITTLE_ENDIAN);

            while (true) {
                
                while (buffer.getInt(OFFSET_FLAG_STARCCM) == 1) {
                    simulation.println("[STAR CCM+] Resuming Simulation");
                    
                    // 读取 6 个螺旋桨的转速 (RPM)
                    double[] rpms = new double[6];
                    for (int i = 0; i < 6; i++) {
                        rpms[i] = buffer.getDouble(OFFSET_RPM_IN + (i * 8));
                    }
                    
                    try {
                        for (int i = 0; i < 6; i++) {
                            String paramName = "RPM_" + i;
                            ScalarGlobalParameter rpmParam = (ScalarGlobalParameter) simulation.get(GlobalParameterManager.class).getObject(paramName);
                            double radPerSec = rpms[i] * (Math.PI / 30.0);
                            rpmParam.getQuantity().setValue(radPerSec); 
                        }
                    } catch (Exception e) {
                        simulation.println("Warrning: can not found RPM Global Parameters");
                    }

                    // 读取 Tethra 计算出的绳缆力 (X, Y, Z)
                    double forceX = -buffer.getDouble(OFFSET_FORCE_IN);
                    double forceY = -buffer.getDouble(OFFSET_FORCE_IN + 8);
                    double forceZ = -buffer.getDouble(OFFSET_FORCE_IN + 16); 
                    ContinuumBody continuumBody = ((ContinuumBody) simulation.get(star.sixdof.BodyManager.class).getObject("MainBody"));
                    ExternalForce externalForce = ((ExternalForce) continuumBody.getExternalForceAndMomentManager().getObject("CableForce"));             
                    Units units_N = ((Units) simulation.getUnitsManager().getObject("N"));
                    externalForce.getForce().setComponentsAndUnits(forceX, forceY, forceZ, units_N);
                    Units units_1 = ((Units) simulation.getUnitsManager().getObject("m"));
                    externalForce.getPositionAsCoordinate().setCoordinate(units_1, units_1, units_1, new DoubleVector(new double[] {-0.22, 0.0, -0.00497}));

                    int t0 = simulation.getSimulationIterator().getCurrentIteration();
                    simulation.getSimulationIterator().step(1);
                    
                    while (simulation.getSimulationIterator().getCurrentIteration() <= t0) {
                        try {
                            Thread.sleep(10);
                        } catch (InterruptedException e) {
                            simulation.println("Interrupted while waiting for step: " + e.getMessage());
                        }
                    }
                    
                    try {
                        double timestamp = simulation.getSolution().getPhysicalTime();

                        double x =  ((Report) simulation.getReportManager().getReport("DisZ")).getReportMonitorValue();
                        double y = -((Report) simulation.getReportManager().getReport("DisY")).getReportMonitorValue(); 
                        double z =  ((Report) simulation.getReportManager().getReport("DisX")).getReportMonitorValue();
                        
                        double roll  =  ((Report) simulation.getReportManager().getReport("rz")).getReportMonitorValue(); 
                        double pitch = -((Report) simulation.getReportManager().getReport("ry")).getReportMonitorValue(); 
                        double yaw   =  ((Report) simulation.getReportManager().getReport("rx")).getReportMonitorValue(); 
                        
                        double u =  ((Report) simulation.getReportManager().getReport("Vrz")).getReportMonitorValue();
                        double v = -((Report) simulation.getReportManager().getReport("Vry")).getReportMonitorValue(); 
                        double w =  ((Report) simulation.getReportManager().getReport("Vrx")).getReportMonitorValue();
                        
                        double p =  ((Report) simulation.getReportManager().getReport("omegarz")).getReportMonitorValue(); 
                        double q = -((Report) simulation.getReportManager().getReport("omegary")).getReportMonitorValue(); 
                        double r =  ((Report) simulation.getReportManager().getReport("omegarx")).getReportMonitorValue();

                        // 严格按照偏移量写入 104 字节 (13 * 8)
                        buffer.putDouble(OFFSET_DATA_START, timestamp);
                        buffer.putDouble(OFFSET_DATA_START + 8, x);
                        buffer.putDouble(OFFSET_DATA_START + 16, y);
                        buffer.putDouble(OFFSET_DATA_START + 24, z);

                        buffer.putDouble(OFFSET_DATA_START + 32, roll);
                        buffer.putDouble(OFFSET_DATA_START + 40, pitch);
                        buffer.putDouble(OFFSET_DATA_START + 48, yaw);

                        buffer.putDouble(OFFSET_DATA_START + 56, u);
                        buffer.putDouble(OFFSET_DATA_START + 64, v);
                        buffer.putDouble(OFFSET_DATA_START + 72, w);

                        buffer.putDouble(OFFSET_DATA_START + 80, p);
                        buffer.putDouble(OFFSET_DATA_START + 88, q);
                        buffer.putDouble(OFFSET_DATA_START + 96, r);

                    } catch (Exception e) {
                        simulation.println("Memory write failed，Please check whether the Report name is correct: " + e.getMessage());
                    }

                    simulation.println("Step Completed");

                    buffer.putInt(OFFSET_FLAG_TETHRA, 1);   
                    buffer.putInt(OFFSET_FLAG_STARCCM, 0); 
		    buffer.force(); // 强制刷入物理内存，确保其他进程可见
                }

                try {
                    Thread.sleep(5);
                } catch (InterruptedException e) {
                    simulation.println("Thread interrupted: " + e.getMessage());
                }
                               
                // 可选的调试输出，频率很高，可以根据需要注释掉
                /*
                MappedByteBuffer readBuffer = buffer.duplicate();
                readBuffer.position(0);
                int flagStarCCM = readBuffer.getInt(OFFSET_FLAG_STARCCM);
                int flagTethra  = readBuffer.getInt(OFFSET_FLAG_TETHRA);
                int flagRovCtrl = readBuffer.getInt(OFFSET_FLAG_ROVCTRL);
                    
                simulation.println(String.format("Flags -> STARCCM: %d | TETHRA: %d | ROVCTRL: %d", 
                                                flagStarCCM, flagTethra, flagRovCtrl));
                */
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
