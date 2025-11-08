#include "Fiber.h"
#include <spdlog/spdlog.h>

// FiberMain::FiberMain()
//     : times(400), Error(1e-10), Nodes(100), TotNoV(1000), TimeStep(20000),
//       DelTime(0.001) {}

FiberMain::FiberMain() {}

FiberMain::~FiberMain() {}

VectorXd FiberMain::initializeTransVal(int index) {
  SPDLOG_DEBUG("Initializing the transient value for index {}", index);
  VectorXd TransVal(TotNoV);
  if (index > 0) {
    FiberRO aa;
    TransVal = aa.ReadTheLastRow(index - 1);
    // cout << TransVal;
  } else {
    VectorXd a = VectorXd::Zero(TotNoV);
    for (int i = 0; i < Nodes; i++) {
        if(i == 0){
        a(i * 10 + 0) = 0.00; // u_0
        a(i * 10 + 1) = 1E-30; // v_0
        a(i * 10 + 2) = 0.00; // w_0
        a(i * 10 + 3) = 3.489 + (Nodes - (i+1)) * 0.065 * 1.21;     // T_0
        a(i * 10 + 4) = 0;     // Sn_0
        a(i * 10 + 5) = 0;     // Sb_0
        a(i * 10 + 6) = 1e-11; // Theta_0
        a(i * 10 + 7) = 1e-11; // Phi_0
        a(i * 10 + 8) = 0.0; // Omega_0
        a(i * 10 + 9) = 0.0; // Omega_0
      }else if(i < Nodes - 1 && i > 0){
        a(i * 10 + 0) = 0.00 + ((0.00 - 0.00) / Nodes) * i; // u
        a(i * 10 + 1) = 1E-30; // v
        a(i * 10 + 2) = 0.00 + ((0.00 - 0.00) / Nodes) * i; // w
        a(i * 10 + 3) = 3.489 + (Nodes - (i+1)) * 0.065 * 1.21;     // T
        a(i * 10 + 4) = 0;     // Sn
        a(i * 10 + 5) = 0;     // Sb
        a(i * 10 + 6) = 1e-11; // Theta
        a(i * 10 + 7) = 1e-11; // Phi
        a(i * 10 + 8) = 1e-11; // Omega
        a(i * 10 + 9) = 1e-11; // Omega
      }else{
        a(i * 10 + 0) = 0.00; // u
        a(i * 10 + 1) = 1E-30; // v
        a(i * 10 + 2) = 0.00; // w
        a(i * 10 + 3) = 3.489;     // T
        a(i * 10 + 4) = 0;     // Sn
        a(i * 10 + 5) = 0;     // Sb
        a(i * 10 + 6) = 1e-11; // Theta
        a(i * 10 + 7) = 1e-11; // Phi
        a(i * 10 + 8) = 0.00; // Omega
        a(i * 10 + 9) = 0.00; // Omega
      }
   }
    TransVal = a;
  }
  return TransVal;
}

MatrixXd FiberMain::initializeZeroMatrix() {
  return MatrixXd::Zero(TimeStep, TotNoV);
}

void FiberMain::Calculation(int index) {
  VectorXd Ynew_current_guess = initializeTransVal(index);
  VectorXd Yold_previous_state = Ynew_current_guess;
  // VectorXd TransVal = initializeTransVal(index);

  cout << endl;
  cout << "Time Step : " << index << "     Now the real time is "
       << index * DelTime << "s";

  Iterator b(Yold_previous_state, Ynew_current_guess, times, Error);
  b.begin(index);

  VectorXd ConvergedY = b.out();

  MatrixXd zero = initializeZeroMatrix();

  if (index > 0) {
    FiberRO bb;
    zero = bb.readCSV(TimeStep);
  }

  for (int j = 0; j < TotNoV; j++) {
    zero(index, j) = ConvergedY(j);
  }

  FiberRO a;
  a.Output(zero, TimeStep, TotNoV);
  // a.OutTopforce(ConvergedY);
  a.OutBottomforce(ConvergedY);
}
