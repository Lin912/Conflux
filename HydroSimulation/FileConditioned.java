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


public class FileConditioned extends StarMacro {

    private static final String FILE_SHARED = "../HydroSimulation/ControlDirect_SharedMemory";
    private static final int OFFSET_PROGRAM_STARCCM = 0;
    private static final int OFFSET_PROGRAM_CITRINE = 4;
    private static final int BUFFER_SIZE = 1024 + 8;
	
	//RAM read point Location
	private static final int OFFSET_DATA_START = 8;
    private static final int OFFSET_FORCE_IN = OFFSET_DATA_START; 
    private static final int OFFSET_DATA_OUT = OFFSET_DATA_START + 24;
	
	
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
                        double forceX = -buffer.getDouble(OFFSET_FORCE_IN);      //  8
						double forceY = -buffer.getDouble(OFFSET_FORCE_IN + 8);  //  16
						double forceZ = -buffer.getDouble(OFFSET_FORCE_IN + 16); //  24

						ContinuumBody continuumBody = ((ContinuumBody) simulation.get(star.sixdof.BodyManager.class).getObject("MainBody"));
						ExternalForce externalForce = ((ExternalForce) continuumBody.getExternalForceAndMomentManager().getObject("CableForce"));
						Units units_0 = ((Units) simulation.getUnitsManager().getObject("N"));
						externalForce.getForce().setComponentsAndUnits(forceX, forceY, forceZ, units_0);
						Units units_1 = ((Units) simulation.getUnitsManager().getObject("m"));
						externalForce.getPositionAsCoordinate().setCoordinate(units_1, units_1, units_1, new DoubleVector(new double[] {-0.22, 0.0, -0.00497}));//Acting point
                        
                        
                        
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
                        
                        //Write to RAM
                        try {
							double vrx = ((Report) simulation.getReportManager().getReport("Vrx")).getReportMonitorValue();
							double vry = ((Report) simulation.getReportManager().getReport("Vry")).getReportMonitorValue();
							double vrz = ((Report) simulation.getReportManager().getReport("Vrz")).getReportMonitorValue();
                        
							double omegarx = ((Report) simulation.getReportManager().getReport("omegarx")).getReportMonitorValue();
							double omegary = ((Report) simulation.getReportManager().getReport("omegary")).getReportMonitorValue();
							double omegarz = ((Report) simulation.getReportManager().getReport("omegarz")).getReportMonitorValue();
							
							double rx = ((Report) simulation.getReportManager().getReport("rx")).getReportMonitorValue();
							double ry = ((Report) simulation.getReportManager().getReport("ry")).getReportMonitorValue();
							double rz = ((Report) simulation.getReportManager().getReport("rz")).getReportMonitorValue();

							int outOffset = OFFSET_DATA_OUT;
							buffer.putDouble(outOffset, vrx);          outOffset += 8;
							buffer.putDouble(outOffset, vry);          outOffset += 8;
							buffer.putDouble(outOffset, vrz);          outOffset += 8;
                        
							buffer.putDouble(outOffset, omegarx);      outOffset += 8;
							buffer.putDouble(outOffset, omegary);      outOffset += 8;
							buffer.putDouble(outOffset, omegarz);      outOffset += 8;
                        
							buffer.putDouble(outOffset, rx);           outOffset += 8;
							buffer.putDouble(outOffset, ry);           outOffset += 8;
							buffer.putDouble(outOffset, rz);
                        
						} catch (Exception e) {
							simulation.println("Writting Warring, get Report: " + e.getMessage());
						}
                        
                        //simulation.saveState("star.sim");
                        simulation.println("Step Completed");

                        buffer.putInt(OFFSET_PROGRAM_CITRINE, 1);
                        buffer.putInt(OFFSET_PROGRAM_STARCCM, 0);
                        buffer.force(); 	                       
                    }

                    try{
                        Thread.sleep(50);
                    } catch(InterruptedException e){
                        simulation.println("Thread interrupted: " + e.getMessage());
                    }
 			                       
                    //simulation.println("Printing Mapped File Content");
                    MappedByteBuffer readBuffer = buffer.duplicate();
                    readBuffer.position(0);
                    int offsetStarCCM = readBuffer.getInt(0);
                    int offsetCitrine = readBuffer.getInt(4);
                        
            }
        }catch(IOException e){
            e.printStackTrace();
        }
    }
}

