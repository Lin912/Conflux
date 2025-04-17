import star.common.*;
import java.io.*;
import java.util.*;
import star.base.neo.*;
import star.sixdof.*;
import star.base.report.*;

import java.io.RandomAccessFile;
import java.nio.MappedByteBuffer;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.ByteOrder;

import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.locks.Condition;

public class FileConditioned extends StarMacro {

    private static final String FILE_PATH_BOTTOMFORCE = "/HydroSimulation/bottomforce.txt";
    private static final String FILE_PATH_VELOCITYR = "/HydroSimulation/VelocityRelative.csv";
    private static final String FILE_PATH_OMEGAR = "/HydroSimulation/omegaRelative.csv";
    private static final String FILE_PATH_EULERANGLE = "/HydroSimulation/EulerAngle.csv";

    private static final String FILE_SHARED = "/HydroSimulation/ControlDirect_SharedMemory";
    private static final int OFFSET_PROGRAM_STARCCM = 0;
    private static final int OFFSET_PROGRAM_CITRINE = 4;
    private static final int BUFFER_SIZE = 1024 + 8;


    @Override
    public void execute() {
        try{
            Simulation simulation = getActiveSimulation();
            
            RandomAccessFile file = new RandomAccessFile(FILE_SHARED, "rw");
            FileChannel channel = file.getChannel();
            MappedByteBuffer buffer = channel.map(FileChannel.MapMode.READ_WRITE,0 ,BUFFER_SIZE);
            buffer.order(ByteOrder.LITTLE_ENDIAN);
            

            while(true){
                
                    while(buffer.getInt(OFFSET_PROGRAM_STARCCM) == 1){
                        simulation.println("[STAR CCM+] Resuming Simulation");
                        
                        //Force input
                        double[] forceComponents = new double[3];
                        try {
                            BufferedReader br = new BufferedReader(new FileReader(FILE_PATH_BOTTOMFORCE));
                            String line = br.readLine();
                        
                            if (line != null) {
                                Scanner scanner = new Scanner(line);
                                for (int i = 0; i < 3; i++) {
                                    if (scanner.hasNextDouble()) {
                                        forceComponents[i] = scanner.nextDouble();
                                    }
                                }
                                scanner.close();
                            }

                        br.close();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                        
                        double forceX = -forceComponents[0];
                        double forceY = forceComponents[1];
                        double forceZ = forceComponents[2];

                        ContinuumBody continuumBody = ((ContinuumBody) simulation.get(star.sixdof.BodyManager.class).getObject("BottomWeight"));//Body's Name
                        ExternalForce externalForce = ((ExternalForce) continuumBody.getExternalForceAndMomentManager().getObject("CableForce"));//Force's Name              
                        Units units_0 = ((Units) simulation.getUnitsManager().getObject("N"));
                        externalForce.getForce().setComponentsAndUnits(forceX, forceY, forceZ, units_0);//Force value
                        Units units_1 = ((Units) simulation.getUnitsManager().getObject("m"));
                        externalForce.getPositionAsCoordinate().setCoordinate(units_1, units_1, units_1, new DoubleVector(new double[] {-0.0465, 0.0, 0.0}));//Force acting point
                        
                        //Running simulation
                        int t0 = simulation.getSimulationIterator().getCurrentIteration();

                        simulation.getSimulationIterator().step(1);
                        
                        while(simulation.getSimulationIterator().getCurrentIteration() <= t0){
                            try{
                                Thread.sleep(50);
                            }catch(InterruptedException e){
                                simulation.println("Interrupted while waiting for step: " + e.getMessage());
                            }
                        }
                        
                        
                        //Write VelocityRelative
                        ReportMonitor reportMonitor_1 = ((ReportMonitor) simulation.getMonitorManager().getMonitor("Vrx"));//Monitor's Name
                        ReportMonitor reportMonitor_2 = ((ReportMonitor) simulation.getMonitorManager().getMonitor("Vry"));//Monitor's Name
                        ReportMonitor reportMonitor_3 = ((ReportMonitor) simulation.getMonitorManager().getMonitor("Vrz"));//Monitor's Name
                        simulation.getMonitorManager().export(FILE_PATH_VELOCITYR, ",", new NeoObjectVector(new Object[] {reportMonitor_1, reportMonitor_2, reportMonitor_3}));//Output fileName
            
                        //Write omegaRelative
                        ReportMonitor reportMonitor_4 = ((ReportMonitor) simulation.getMonitorManager().getMonitor("omegarx"));//Monitor's Name
                        ReportMonitor reportMonitor_5 = ((ReportMonitor) simulation.getMonitorManager().getMonitor("omegary"));//Monitor's Name
                        ReportMonitor reportMonitor_6 = ((ReportMonitor) simulation.getMonitorManager().getMonitor("omegarz"));//Monitor's Name
                        simulation.getMonitorManager().export(FILE_PATH_OMEGAR, ",", new NeoObjectVector(new Object[] {reportMonitor_4, reportMonitor_5, reportMonitor_6}));//Output fileName
            
                        //Write EulerAngle
                        ReportMonitor reportMonitor_7 = ((ReportMonitor) simulation.getMonitorManager().getMonitor("rx"));//Monitor's Name
                        ReportMonitor reportMonitor_8 = ((ReportMonitor) simulation.getMonitorManager().getMonitor("ry"));//Monitor's Name
                        ReportMonitor reportMonitor_9 = ((ReportMonitor) simulation.getMonitorManager().getMonitor("rz"));//Monitor's Name
                        simulation.getMonitorManager().export(FILE_PATH_EULERANGLE, ",", new NeoObjectVector(new Object[] {reportMonitor_7, reportMonitor_8, reportMonitor_9}));//Output fileName


                        simulation.println("Step Completed");

                        buffer.putInt(OFFSET_PROGRAM_CITRINE, 1);
                        buffer.putInt(OFFSET_PROGRAM_STARCCM, 0);
                        buffer.force();                            
                    }

                    try{
                        Thread.sleep(1000);
                    } catch(InterruptedException e){
                        simulation.println("Thread interrupted: " + e.getMessage());
                    }
                        
                    simulation.println("Printing Mapped File Content");
                    MappedByteBuffer readBuffer = buffer.duplicate();
                    readBuffer.position(0);
                    int offsetStarCCM = readBuffer.getInt(0);
                    int offsetCitrine = readBuffer.getInt(4);
                        
                    simulation.println("OFFSET_PROGRAM_STARCCM" + offsetStarCCM);
                    simulation.println("OFFSET_PROGRAM_CITRINE" + offsetCitrine);
                    simulation.println("[STAR CCM+] Pausing Simulation");
                    // simulation.getSimulationIterator().stop();
            }
        }catch(IOException e){
            e.printStackTrace();
        }
    }
}

