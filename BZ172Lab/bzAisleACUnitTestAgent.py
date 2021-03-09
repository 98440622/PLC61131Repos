# -*- coding: utf-8 -*-
"""
Test agent and cases for bzAisleACUnit project.

Created on Tue Mar  9 11:52:24 2021

@author: BoTong ZHANG
"""

# %% bzAisleACUnit test cases
from bzAisleACUnit import *
import threading
import heapq
from queue import Queue
import time
from datetime import datetime

class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._count = 0
        self._cv = threading.Condition()

    def put(self, item, priority):
        with self._cv:
            heapq.heappush(self._queue, (-priority, self._count, item))
            self._count += 1
            self._cv.notify()

    def get(self):
        with self._cv:
            while len(self._queue) == 0:
                self._cv.wait()
            return heapq.heappop(self._queue)[-1]

class bzAisleACUnitTestAgent:
    """
    Useage :

        # create the unit (connect to data point agent)
        unit = bzAisleACUnit()

        # create test agent
        tester = bzAisleACUnitTestAgent(unit)

        # start a background thread to process periodical requests and user reqs
        mytester.start()

        # poll a data point
        mytester.execute(unit.UpperReturnAirTemperature)

        # update a data point
        mytester.execute(unit.UnitModeCfg, 1)

        # call a predefined bunch of commands
        mytester.getFMVersion()

        ...

        # stop the test agent
        mytest.stop()

    """
    def __init__(self, unit):
        self.unit = unit
        self.is_started = False
        self.req_q = Queue()
        self.rpl_q = Queue()
        self.lines_of_buffer = 0
        
    def __del__(self):
        if (self.is_started):
            self.stop()
        else:
            pass

    def __run_at_1Hz(self):
        dt = datetime.now()
        dt_fmt = "{0:02d}-{1:02d} {2:02d}:{3:02d}:{4:02d}"
        dt_str = "{0}{1:02d}{2:02d}_{3:02d}{4:02d}{5:02d}".format(dt.year,
                                                                  dt.month,
                                                                  dt.day,
                                                                  dt.hour,
                                                                  dt.minute,
                                                                  dt.second)
        with open("bzAisleACUnitTestLog_{0}.log".format(dt_str), "w") as file:
            print("tester background task is started")
            file.write('DateTime,\n')
            while (self.is_started):
                while (not self.req_q.empty()):
                    obj = self.req_q.get_nowait()
                    if (len(obj) == 1):
                        # read
                        self.rpl_q.put(obj[0]())
                    elif (len(obj) == 2):
                        self.rpl_q.put(obj[0](obj[1]))
                    else:
                        pass
                dt = datetime.now()
                strLn = dt_fmt.format(dt.month,
                                      dt.day,
                                      dt.hour,
                                      dt.minute,
                                      dt.second)
                strLn += ',\n'
                # todo : add periodical data log...
                file.write(strLn)
                
                if (self.lines_of_buffer >= 5 * 60):
                    self.lines_of_buffer = 0
                    
                    file.flush()
                else:
                    self.lines_of_buffer += 1
                
                time.sleep(1) # 1 Hz

            file.close()
            print('tester background task is done')

    def start(self):
        if (not self.is_started):
            self.is_started = True
            self.task = threading.Thread(name='__run_at_1Hz',
                                         target=self.__run_at_1Hz)
            self.task.start()
        else:
            print('agent is started, stop first and start again')

    def stop(self):
        self.is_started = False
        self.task.join()

    def execute(self, obj, *args):
        if (self.is_started):
            if (args == ()):
                self.req_q.put([obj])
            else:
                self.req_q.put([obj, args[0]])

            print(self.rpl_q.get())
        else:
            print('call start() firstly')
            
    def initSoloMode(self):
        if (not self.execute(self.unit.BZIsRealMode)):
            self.execute(self.unit.BZAIL_01, 200)
            self.execute(self.unit.BZAIL_02, 210)
            self.execute(self.unit.BZAIL_03, 180)
            self.execute(self.unit.BZAIL_04, 185)
            self.execute(self.unit.BZAIL_05, 182)
            self.execute(self.unit.BZAIL_06, 180)
            self.execute(self.unit.BZAIL_07, 230)
            self.execute(self.unit.BZAIL_10, 278)
        else:
            print("Set controller solot mode first, then we talk")

    def getFMVersion(self):
        self.req_q.put([self.unit.BIOSVersion])
        self.req_q.put([self.unit.AppVersion])
        res = []
        while (not self.rpl_q.empty):
            res.append(self.rpl_q.get())
        return res

    def setUnit(self, mode):
        is_cmd = True
        if (mode == 'off'):
            self.req_q.put([self.unit.UnitModeCfg, 0])
        elif (mode == 'on'):
            self.req_q.put([self.unit.UnitModeCfg, 1])
        elif (mode == 'man'):
            self.req_q.put([self.unit.UnitModeCfg, 2])
        else:
            is_cmd = False
            print(mode, ' is not a valid command')

        if (is_cmd):
            print(self.rpl_q.get())
        else:
            pass

    # def getAmibentTemperatures(self):
    #     return [self.unit.AverageReturnAirTemperature(),
    #             self.unit.AverageSupplyAirTemperature(),
    #             self.unit.RackInletAirTemperatureAlfa(),
    #             self.unit.RackInletAirTemperatureBravo(),
    #             self.unit.MaxRackInletAirTemperature()]



# %% (OBSOLETE) Solo is what i want
class BZ172Lab :
    def __init__(self):
        self.caller = IrACdx36LibCaller()

        self.IDandVars = pd.read_csv('BZ172LabDDF.csv', usecols=[0, 2])
        self.IDandVars.NO = self.IDandVars.NO - 1

        self.BIOSVersionID,\
        self.AppVersionID = [
            self.IDandVars.NO[self.IDandVars.DataPoint == 'BIOSVersion'],
            self.IDandVars.NO[self.IDandVars.DataPoint == 'AppVersion']]
        self.BZIsRealModeID = \
            self.IDandVars.NO[self.IDandVars.DataPoint == 'BZIsRealMode']

        self.BZDILnID = [x for x in range(84, 96)]
        self.BZAILnID = [x for x in range(96, 108)]

        self.AmbientTemperaturesID = [x for x in range(2, 11)]

        self.WarningIDs = [x for x in range(38, 66)] # 65 is the last one
        self.AlarmIDs = [x for x in range(66, 77)]

        self.ActuatorIDs = [x for x in range(12, 20)]

        if (self.caller.init() != 0):
            print("Activate IrACdx36 firstly.")
        else:
            var = self.caller.getVar(self.BZIsRealModeID)
            if (var[0] != 0):
                print("IrACdx36 cannot connect to target.")
            else:
                print("GOOD to go with {0} mode".format(
                    ['REAL', 'SOLO'][int(var[1]) == 0]))
                # ['true', 'false'][True]  'false'

        print("BIOS         : ",
              (self.caller.getStr(self.BIOSVersionID)[1]))
        print("APPLICATION  : ",
              (self.caller.getStr(self.AppVersionID)[1]))

    def __del__(self):
        #self.caller.term()
        pass

    def checkVars(self, ids):
        if (type(ids) == int):
            res = self.caller.getVar(ids)
            print("{0}({2})={1}".format(self.IDandVars.DataPoint[ids],
                                        res[1],
                                        ids))
        else:
            tmps = self.caller.getVars(ids)
            for i, k in zip(ids, range(0, len(ids))):
                print("{0}({1}) = {2}".format(self.IDandVars.DataPoint[i],
                                              k,
                                              tmps[k][1]))

    def updateVar(self, i, v):
        if (i in self.IDandVars.NO):
            self.caller.setVar(i, v)
        else:
            print(i, ' is out of boundary')

    def goSolo(self):
        var = self.caller.getVar(self.BZIsRealModeID)
        if (int(var[0]) != 0):
            print("Lost target!")
        else:
            if (int(var[1]) == 1):
                #print("Set target in solo mode")
                self.caller.setVar(self.BZIsRealModeID, 0)
                input("Cycle the power of the target and "
                      "press any key after it reboot...")
                self.caller.reset()
            else:
                pass

            for i in self.BZAILnID:
                self.caller.setVar(i, 220)

            print("Solo is my desire.")

    def setAI(self, i, v):
        if (i in self.BZAILnID):
            self.caller.setVar(i, v)
        else:
            print(i, " is not for AI index")

    def toggleDI(self, i):
        if (i in self.BZDILnID):
            self.caller.setVar(i, [1, 0][self.caller.getVar(i)[1] == 0])

    def checkAmbient(self):
        tmps = self.caller.getVars(self.AmbientTemperaturesID)
        for i, k in zip(self.AmbientTemperaturesID,
                        range(0, len(self.AmbientTemperaturesID))):
            print("{0}({2}) = {1:.01f}".format(self.IDandVars.DataPoint[i],
                                          tmps[k][1],
                                          k))

    def checkWarnings(self):
        tmps = self.caller.getVars(self.WarningIDs)
        for i, k in zip(self.WarningIDs, range(0, len(self.WarningIDs))):
            print("{0} = {1}".format(self.IDandVars.DataPoint[i],
                                     ['NO', 'YES'][int(tmps[k][1])],
                                     k))

    def checkAlarms(self):
        tmps = self.caller.getVars(self.AlarmIDs)
        for i, k in zip(self.AlarmIDs, range(0, len(self.AlarmIDs))):
            print("{0} = {1}".format(self.IDandVars.DataPoint[i],
                                     ['NO', 'YES'][int(tmps[k][1])],
                                     k))

    def checkActuators(self):
        self.checkVars(self.ActuatorIDs)

# %% (OBSOLETE) an example of how to use a script to run an auto testing
def sample_1():
    RATavg, SATavg, RACmax, Unitst, Unitcmd, Coolsp, SATsp, Fanstg = \
        [4,      7,     10,     12,      80,     81,    83,     97]
    EvapFancmd, EXVcmd, Compcmd, Compspd = \
        [   13,     14,      15,      19]

    caller.init()

    print("TEST CASE 1. Cooling function verification")

    print("Step 1. check ambient temperature")
    print("Average supply air temperature is ", caller.getVar(SATavg)[1])
    print("Average return air temperature is ", caller.getVar(RATavg)[1])
    print("Max rack inlet temperature is ", caller.getVar(RACmax)[1])

    print("Step 2. make sure the set points can meet the requirements")
    print("Supply air setpoint is 15.0")
    caller.setVar(SATsp, 15.0)
    print("Fan strategy is 0 (inrow)")
    caller.setVar(Fanstg, 0)
    print("Cool setpoint is 18.0")
    caller.setVar(Coolsp, 18.0)

    print("Step 3. set unit on (1)")
    caller.setVar(Unitcmd, 1)
    time.sleep(1) # wait for 1 second
    print("<<{0}>> - Unit status is ON?".format(
        caller.getVar(Unitst) == (0, 2)))

    time.sleep(5)
    print("Step 4. check actuators")
    print("<<{0}>> - Evaporator fan is started?".format(
        caller.getVar(EvapFancmd)[1] > 0))
    print("<<{0}>> - EXV is opened?".format(
        caller.getVar(EXVcmd)[1] > 0))
    print("Wait for 10 seconds...")
    time.sleep(10)
    print("<<{0}>> - Compressor is started?".format(
        caller.getVar(Compcmd)[1] > 0))

    print("Step 5. check compressor upload")
    comp_spd = caller.getVar(Compcmd)[1]
    print("Compressor current speed ", comp_spd)
    print("Wait for 20 second...")
    time.sleep(20)
    print("<<{0}>> - Now the compressor speed is increased?".format(
        caller.getVar(Compcmd)[1] > comp_spd))

    print("Step 6. set unit off")
    caller.setVar(Unitcmd, 0)
    print("Wait for 10 seconds...")
    time.sleep(10)
    print("<<{0}>> - All actuators are off".format(
        caller.getVar(EvapFancmd)[1] == 0 and
        caller.getVar(EXVcmd)[1] == 0) and
        caller.getVar(Compcmd)[1] == 0)

    print("END OF TEST CASE 1")

    caller.term()
    print("Disconnect from data point agent")

