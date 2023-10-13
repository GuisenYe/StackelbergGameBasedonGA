import gurobipy as gurobi
from gurobipy import GRB


def gurobiFunction(price,purchasingPrice):
    # 定义负载

    print("the input price is:")
    print(price)
    LInterActive0 = [1.5, 1.95, 2.325, 0.075, 0.45, 0.975, 2.4, 2.7, 3.665, 4.425, 4.575, 5.25, 5.475, 4.35, 3.45, 2.7,
                     1.825, 1.25, 2.25, 2.175, 2.7, 1.25, 2.05, 2.55]
    batchwork1 = 36
    batchwork2 = 2
    batchwork3 = 2
    # 定义储能
    EnergyStorageMax = 30
    EnergyStorageMin = 5
    ChargeEff = 0.8
    Pchargemax = 5

    # 定义了gas/coal两种发电机的运行特征；
    PoMaxGas = 15
    PoMinGas = 3
    RampRateGas = 3
    InterAMinOnOffTimeGas = 3
    NoLoadCostGas = 32
    ShutCostGas = 45
    MarginCostGas = 42
    InitPoGas = 9

    PoMaxCoal = 18
    PoMinCoal = 9
    RampRateCoal = 6
    InterAMinOnOffTimeCoal = 2
    NoLoadCostCoal = 30
    ShutCostCoal = 40
    MarginCostCoal = 30
    InitPoCoal = 11

    # 定义风电、光伏装机容量，和当地当天的电价、风光出力占比；
    SolarCap = 10
    WindCap = 10
    PriceRate = 1.5
    CAPrice=[i  for i in price]



    CASolarRate = [0, 0, 0, 0, 0, 0, 0, 0, 0.00460000000000000, 0.112700000000000, 0.265800000000000, 0.392000000000000,
                   0.464800000000000, 0.524300000000000, 0.535700000000000, 0.530400000000000, 0.497200000000000,
                   0.428700000000000, 0.333600000000000, 0.224100000000000, 0.0873000000000000, 0.000500000000000000, 0,
                   0]
    CAWindRate = [0.215600000000000, 0.234500000000000, 0.181500000000000, 0.192200000000000, 0.192900000000000,
                  0.188000000000000, 0.190500000000000, 0.173300000000000, 0.158100000000000, 0.106500000000000,
                  0.0939000000000000, 0.141400000000000, 0.132400000000000, 0.134700000000000, 0.232300000000000,
                  0.232000000000000, 0.228800000000000, 0.247000000000000, 0.274600000000000, 0.228600000000000,
                  0.231200000000000, 0.257700000000000, 0.268800000000000, 0.288300000000000]

    CASolar = [i * SolarCap for i in CASolarRate]
    CAWind = [i * WindCap for i in CAWindRate]
    # CAPrice=[i*PriceRate  for i in CAPrice0]

    LInterActive = [i / 2 for i in LInterActive0]
    # create a new model
    Model = gurobi.Model("qp")
    # define variable
    # BATCH  WORKLOAD

    # CAPrice = Model.addVars(24, vtype=GRB.CONTINUOUS, name="price")
    batchUPSA1Task1 = Model.addVars(24, vtype=GRB.CONTINUOUS, name="batchUPSA1Task1")

    # INTERACTIVE WORKLOAD
    interActiveA1 = Model.addVars(24, vtype=GRB.CONTINUOUS, name="interActiveA1")

    # TOTAL TASK
    TotalTaskA1 = Model.addVars(24, vtype=GRB.CONTINUOUS, name="TotalTaskA1")

    # TOTAL POWER SERVER
    UPSOutPowerA1 = Model.addVars(24, vtype=GRB.CONTINUOUS, name="UPSOutPowerA1")

    # RENEW POWER THROUGH AWAY
    PrenewableThroughAwayA = Model.addVars(24, vtype=GRB.CONTINUOUS, name="PrenewableThroughAwayA")

    # 还差：电池模型、电机模型、Pgrid；
    # BATTERY MODEL
    PchargeA = Model.addVars(24, vtype=GRB.CONTINUOUS, name="PchargeA")
    PdischargeA = Model.addVars(24, vtype=GRB.CONTINUOUS, name="PdischargeA")
    ZchargeA = Model.addVars(24, vtype=GRB.BINARY, name="ZchargeA")
    ZdischargeA = Model.addVars(24, vtype=GRB.BINARY, name="ZdischargeA")
    EnergyStorageStateA = Model.addVars(24, vtype=GRB.CONTINUOUS, name="EnergyStorageStateA")

    # CONVENTIONAL GENERATOR MODEL
    PunitA1 = Model.addVars(24, vtype=GRB.CONTINUOUS, name="PunitA1")
    opA1 = Model.addVars(24, vtype=GRB.BINARY, name="opA1")
    upA1 = Model.addVars(24, vtype=GRB.BINARY, name="upA1")
    downA1 = Model.addVars(24, vtype=GRB.BINARY, name="downA1")

    PunitA2 = Model.addVars(24, vtype=GRB.CONTINUOUS, name="PunitA2")
    opA2 = Model.addVars(24, vtype=GRB.BINARY, name="opA2")
    upA2 = Model.addVars(24, vtype=GRB.BINARY, name="upA2")
    downA2 = Model.addVars(24, vtype=GRB.BINARY, name="downA2")

    # unit cost
    UnitCostA1 = Model.addVars(24, vtype=GRB.CONTINUOUS, name="UnitCostA1")
    UnitCostA2 = Model.addVars(24, vtype=GRB.CONTINUOUS, name="UnitCostA2")

    # UPS INPUT POWER
    PupsInA1 = Model.addVars(24, vtype=GRB.CONTINUOUS, name="PupsInA1")

    # Pgrid SERVER
    PgridA = Model.addVars(24, vtype=GRB.CONTINUOUS, name="PgridA")

    # set objective
    obj = gurobi.QuadExpr()
    for i in range(24):
        obj.add(PgridA[i] * CAPrice[i] + UnitCostA1[i] + UnitCostA2[i])
        # obj.add(PgridA[i] * CAPrice[i] + UnitCostA1[i] + UnitCostA2[i]+20*PunitA1[i]*413/1000+20*PunitA2[i]*995/1000)

    Model.setObjective(obj, GRB.MINIMIZE)

    # ADD CONSTRAINT

    for i in range(24):
        Model.addConstr(batchUPSA1Task1[i] >= 0, "A1 batch workload 1 down bound" + str(i))

        # UPS TOTAL WORK CONSTRAINT
        Model.addConstr(TotalTaskA1[i] == batchUPSA1Task1[i] + interActiveA1[i],
                        "A1 total workload constraint hour" + str(i))

        # UPS TOTAL WORK UP BOUND CONSTRAINT
        Model.addConstr(TotalTaskA1[i] <= 3.6, "A1 workload up bound" + str(i))

        Model.addConstr(TotalTaskA1[i] >= 0, "A1 workload down bound" + str(i))

        # UPS TOTAL POWER CONSTRAINT
        Model.addConstr(UPSOutPowerA1[i] == TotalTaskA1[i] * 10, "A1 power expression hour" + str(i))

        # UPS TOTAL INPUT POWER CONSTRAINT
        Model.addConstr(PupsInA1[i] == UPSOutPowerA1[i] * 1.3, "A1 input power expression hour" + str(i))

        Model.addConstr(UnitCostA1[i] == MarginCostGas * PunitA1[i] + ShutCostGas * upA1[i] + ShutCostGas * downA1[
            i] + NoLoadCostGas * opA1[i], "A1 generator constraint")
        Model.addConstr(UnitCostA2[i] == MarginCostCoal * PunitA2[i] + ShutCostCoal * upA2[i] + ShutCostCoal * downA2[
            i] + NoLoadCostCoal * opA2[i], "A2 generator constraint")

        # TOTAL INTERACTIVE WORK CONSTRAINT
        Model.addConstr(interActiveA1[i] == LInterActive[i],
                        "Total interactive work constraint hour" + str(i))
        Model.addConstr(
            PgridA[i] == PupsInA1[i] + PrenewableThroughAwayA[i] - CASolar[i] - CAWind[i] + ZchargeA[i] * PchargeA[i] -
            ZdischargeA[i] * PdischargeA[i] - PunitA1[i] - PunitA2[i], "grid A power expression hour" + str(i))

        Model.addConstr(PgridA[i] >= 0, "no flow to grid constraintA ")

        Model.addConstr(PrenewableThroughAwayA[i] >= 0, "renewable through out constraintA ")

    # TOTAL BATCH WORKLOAD CONSTRAINT
    Model.addConstr(batchUPSA1Task1.sum() == batchwork1, "Total batch workload constraint")

    # ESS CONSTRAINT
    Model.addConstr(EnergyStorageStateA[0] == 5, "ESS A init state Constraint")
    Model.addConstr(EnergyStorageStateA[23] == 5, "ESS A final state Constraint")

    for i in range(24):
        Model.addConstr(PchargeA[i] <= 5 * ZchargeA[i], "ESS A max charge power Constraint")
        Model.addConstr(PchargeA[i] >= 0, "ESS A min charge power Constraint")
        Model.addConstr(PdischargeA[i] <= 5 * ZdischargeA[i], "ESS A max discharge power Constraint")
        Model.addConstr(PdischargeA[i] >= 0, "ESS A min discharge power Constraint")
        Model.addConstr(ZchargeA[i] <= 1, "ESS A  charge state Constraint")
        Model.addConstr(ZchargeA[i] >= 0, "ESS A  charge state Constraint")
        Model.addConstr(ZdischargeA[i] <= 1, "ESS A  discharge state Constraint")
        Model.addConstr(ZchargeA[i] + ZdischargeA[i] <= 1, "ESS A  charge discharge state Constraint")
        Model.addConstr(EnergyStorageStateA[i] >= 5, "ESS A max storage Constraint")
        Model.addConstr(EnergyStorageStateA[i] <= 30, "ESS A min storage Constraint")
        # Model.addConstr(PchargeA[i] * PdischargeA[i] == 0, "ESS A charge state Constraint")

    for i in range(23):
        Model.addConstr(
            EnergyStorageStateA[i + 1] == EnergyStorageStateA[i] + 0.8 * ZchargeA[i] * PchargeA[i] - 0.8 * ZdischargeA[
                i] * PdischargeA[i], "ESS A storage state expression Constraint")

    # CONVENTIONAL GENERATOR CONSTRAINT
    # STATE INDICATOR
    for i in range(24):
        Model.addConstr(PunitA1[i] >= 0, "generator A1 >0 Constraint1")
        Model.addConstr(opA1[i] >= 0, "generator A1 open Constraint1")
        Model.addConstr(opA1[i] <= 1, "generator A1 open Constraint2")
        Model.addConstr(upA1[i] >= 0, "generator A1 up Constraint1")
        Model.addConstr(upA1[i] <= 1, "generator A1 up Constraint2")
        Model.addConstr(downA1[i] >= 0, "generator A1 down Constraint1")
        Model.addConstr(downA1[i] <= 1, "generator A1 down Constraint2")

        Model.addConstr(PunitA2[i] >= 0, "generator A2 >0 Constraint1")
        Model.addConstr(opA2[i] >= 0, "generator A2 open Constraint1")
        Model.addConstr(opA2[i] <= 1, "generator A2 open Constraint2")
        Model.addConstr(upA2[i] >= 0, "generator A2 up Constraint1")
        Model.addConstr(upA2[i] <= 1, "generator A2 up Constraint2")
        Model.addConstr(downA2[i] >= 0, "generator A2 down Constraint1")
        Model.addConstr(downA2[i] <= 1, "generator A2 down Constraint2")

    # MAX MIN POWER
    for i in range(24):
        Model.addConstr(PunitA1[i] >= PoMinGas * opA1[i], "generator A1 min power Constraint1")
        Model.addConstr(PunitA1[i] <= PoMaxGas * opA1[i], "generator A1 max power Constraint1")

        Model.addConstr(PunitA2[i] >= PoMinCoal * opA2[i], "generator A2 min power Constraint1")
        Model.addConstr(PunitA2[i] <= PoMaxCoal * opA2[i], "generator A2 max power Constraint1")

    # INIT STATE
    Model.addConstr(PunitA1[0] == 0, "generator A1 init  power Constraint1")
    Model.addConstr(opA1[0] == 0, "generator A1 init  on state Constraint1")
    Model.addConstr(upA1[0] == 0, "generator A1 init  up state Constraint1")
    Model.addConstr(downA1[0] == 0, "generator A1 init  down state Constraint1")

    Model.addConstr(PunitA2[0] == 0, "generator A2 init  power Constraint1")
    Model.addConstr(opA2[0] == 0, "generator A2 init  on state Constraint1")
    Model.addConstr(upA2[0] == 0, "generator A2 init  up state Constraint1")
    Model.addConstr(downA2[0] == 0, "generator A2 init  down state Constraint1")

    # START/SHUT DOWN TIME
    for i in range(1, 24):
        for j in range(i + 1, i + InterAMinOnOffTimeGas):
            if j <= 23:
                Model.addConstr(-opA1[i - 1] + opA1[i] - opA1[j] <= 0, "generator A1 start up time  Constraint1")
                Model.addConstr(opA1[i - 1] - opA1[i] + opA1[j] <= 1, "generator A1 shut down time  Constraint1")

    for i in range(1, 24):
        for j in range(i + 1, i + InterAMinOnOffTimeCoal):
            if j <= 23:
                Model.addConstr(-opA2[i - 1] + opA2[i] - opA2[j] <= 0, "generator A2 start up time  Constraint1")
                Model.addConstr(opA2[i - 1] - opA2[i] + opA2[j] <= 1, "generator A2 shut down time  Constraint1")

    # RAMPING UP/DOWN CONSTRAINT
    for i in range(1, 24):
        Model.addConstr(-opA1[i - 1] + opA1[i] - upA1[i] <= 0, "generator A1 ramp up time  Constraint1")
        Model.addConstr(opA1[i - 1] - opA1[i] - downA1[i] <= 0, "generator A1 ramp down time  Constraint1")

        Model.addConstr(-opA2[i - 1] + opA2[i] - upA2[i] <= 0, "generator A2 ramp up time  Constraint1")
        Model.addConstr(opA2[i - 1] - opA2[i] - downA2[i] <= 0, "generator A2 ramp down time  Constraint1")

    # # RAMPING RATE CONSTRAINT
    for i in range(1, 24):
        Model.addConstr(PunitA1[i] - PunitA1[i - 1] <= (2 - opA1[i - 1] - opA1[i]) * PoMinGas + (
                    1 + opA1[i - 1] - opA1[i]) * RampRateGas, "generator A1 ramp rate  Constraint1")
        Model.addConstr(-PunitA1[i] + PunitA1[i - 1] <= (2 - opA1[i - 1] - opA1[i]) * PoMinGas + (
                    1 - opA1[i - 1] + opA1[i]) * RampRateGas, "generator A1 ramp rate  Constraint2")

        Model.addConstr(PunitA2[i] - PunitA2[i - 1] <= (2 - opA2[i - 1] - opA2[i]) * PoMinCoal + (
                    1 + opA2[i - 1] - opA2[i]) * RampRateCoal, "generator A2 ramp rate  Constraint1")
        Model.addConstr(-PunitA2[i] + PunitA2[i - 1] <= (2 - opA2[i - 1] - opA2[i]) * PoMinCoal + (
                    1 - opA2[i - 1] + opA2[i]) * RampRateCoal, "generator A2 ramp rate  Constraint2")

    Model.Params.NonConvex = 2
    # Model.Params.TimeLimit=300
    Model.Params.MIPGap = 0.00005
    # Model.Params.DualReductions=0
    Model.optimize()

    totalenergy = 0
    if Model.status == GRB.Status.INFEASIBLE:
        print("optimization was stopped with status is: Infeasible")
        Model.computeIIS()
        print("this constraint is infeasible")
        for c in Model.getConstrs():
            if c.IISConstr:
                print('%s' % c.constrName)
    print("xxx model.objxxx")
    print(Model.getObjective().getValue())
    Ppurchase=[]

    for i in range(24):
        Ppurchase.append(PgridA[i].x)
    print("the grid get this income from electricity trading")
    GridBonus=0
    for i in range(24):
        GridBonus += Ppurchase[i] * (CAPrice[i] - purchasingPrice[i])
    print(GridBonus)
    print("the power purchased from grid")
    print(Ppurchase)
    Pserver=[]
    Pgenerator=[]
    Prenew=[]
    Prenwthrou=[]

    for i in range(24):
        Pserver.append(PupsInA1[i].x)
        Pgenerator.append(PunitA1[i].x+PunitA2[i].x)
        Prenew.append(CAWind[i]+CASolar[i])
        Prenwthrou.append(PrenewableThroughAwayA[i].x)
    print("Pserver")
    print(Pserver)
    print("Pgenerator")
    print(Pgenerator)
    print("Prenew")
    print(Prenew)
    print("Pthrough")
    print(Prenwthrou)

    return Ppurchase

