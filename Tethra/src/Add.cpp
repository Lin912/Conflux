#include "Add.h"

Add::Add(const VectorXd &arr, const VectorXd &brr, int index):Yold(arr), Ynew(brr)
{

    FiberRO a;
    PhysicalData physicalData = ParaReader::ReadAllPhysicalData(a, index);
    Vtx = physicalData.Vtx;
    Vty = physicalData.Vty;
    Vtz = physicalData.Vtz;

    Vbx = physicalData.Vbx;
    Vby = physicalData.Vby;
    Vbz = physicalData.Vbz;

    // Timestep = physicalData.TS;
    // Nodes = physicalData.NODES;
    // Variables = physicalData.VARIABLES;
    // TnoV = physicalData.TNOV;
}

Add::~Add() {}

Vector3d Add::calculatePoint00(const VectorXd& Y)
{
    Vector3d point;
    point(0) = Vtx * cos(Y(7)) * cos(Y(6)) + Vty * cos(Y(6)) * sin(Y(7)) - Vtz * sin(Y(6));
    point(1) = Vty * cos(Y(7)) - Vtx * sin(Y(7));
    point(2) = Vtx * cos(Y(7)) * sin(Y(6)) + Vty * sin(Y(6)) * sin(Y(7)) + Vtz * cos(Y(6));
    return point;
}

Vector3d Add::calculatePoint02(const VectorXd& Y)
{
    Vector3d point;
    point(0) = Vbx*cos(Y(Variables*(Nodes-1)+7))*cos(Y(Variables*(Nodes-1)+6)) + Vby*cos(Y(Variables*(Nodes-1)+6))*sin(Y(Variables*(Nodes-1)+7)) - Vbz*sin(Y(Variables*(Nodes-1)+6));
    point(1) = Vby*cos(Y(Variables*(Nodes-1)+7)) - Vbx*sin(Y(Variables*(Nodes-1)+7));
    point(2) = Vbx*cos(Y(Variables*(Nodes-1)+7))*sin(Y(Variables*(Nodes-1)+6)) + Vby*sin(Y(Variables*(Nodes-1)+6))*sin(Y(Variables*(Nodes-1)+7)) + Vbz*cos(Y(Variables*(Nodes-1)+6));
    return point;
}

VectorXd Add::Addyold()
{
    VectorXd temp(TnoV);

    Vector3d point00 = calculatePoint00(Yold);
    VectorXd point01(2);
    point01.setZero();
    Vector3d point02 = calculatePoint02(Yold);
    VectorXd point03(2);
    point03.setZero();

    temp.segment(0, 3) = point00;
    temp.segment(3, 5) = Yold.segment(3, 5);
    temp.segment(8, 2) = point01;
    temp.segment(10, TnoV-20) = Yold.segment(10, TnoV-20);
    temp.segment(TnoV-10, 3) = point02;
    temp.segment(TnoV-7, 5) = Yold.segment(TnoV-7, 5);
    temp.tail(2) = point03;

    return temp;
}

VectorXd Add::Addynew()
{
    VectorXd temp(TnoV);

    Vector3d point00 = calculatePoint00(Ynew);
    VectorXd point01(2);
    point01.setZero();
    Vector3d point02 = calculatePoint02(Ynew);
    VectorXd point03(2);
    point03.setZero();

    temp.segment(0, 3) = point00;
    temp.segment(3, 5) = Ynew.segment(3, 5);
    temp.segment(8, 2) = point01;
    temp.segment(10, TnoV-20) = Ynew.segment(10, TnoV-20);
    temp.segment(TnoV-10, 3) = point02;
    temp.segment(TnoV-7, 5) = Ynew.segment(TnoV-7, 5);
    temp.tail(2) = point03;

    return temp;
}
