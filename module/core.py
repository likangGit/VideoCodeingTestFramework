
import os
from itertools import product
import multiprocessing
from multiprocessing import cpu_count
from abc import ABC, abstractmethod
class Operator(ABC):

    @abstractmethod
    def operate(input_dir, output_dir):
        pass

REGISTER = {}
def FUNCTION_REGISTER(stageName, methodName, methodClass, useMultiProcessing=True):
    if stageName in REGISTER:
        REGISTER[stageName].update({methodName:{'class': methodClass, 'useMP':useMultiProcessing} })
    else:
        REGISTER.update({stageName:{methodName: {'class':methodClass, 'useMP':useMultiProcessing} } })

def parseParameters(inputs, parameters):
    pks, pvs = ['input'], [inputs,]
    for pk, pv in parameters.items():
        pks.append(pk)
        pvs.append(pv if isinstance(pv,list) else [pv,])
    pvs = list(product(*pvs) )
    return [dict(zip(pks, pv)) for pv in pvs]

def Exec(config):
    
    input_dir = config.pop('inputFolder')
    inputs = os.listdir(input_dir)
    for stageName, stageV in config.items():
        print('---------------{}-----------------'.format(stageName))
        assert stageName in REGISTER, 'This stage not be registed'
        assert len(inputs)>0, 'No input'
        stage = REGISTER[stageName]
        output_list = []
        for methodName, methodParams in stageV.items():
            methodParams = parseParameters(inputs, methodParams)
            methodClass = stage[methodName]['class']
            methodUseMP = stage[methodName]['useMP']
            #每个method使用线程池，不清楚线程是close是否还能再open，所以每次重新申请
            pool = multiprocessing.Pool(processes=cpu_count())
            #TODO 还需要解决一下output路径函数内不能随意定义问题。
            for param in methodParams:
                output = ''
                for pk,pv in param.items():
                    output += '_'.join([pk, str(pv)])+'_'
                print("parameters:",param)
                input_file = param.pop('input')
                instance_op = methodClass(**param)
                if methodUseMP:
                    pool.apply_async(instance_op.operate, args=(input_file, output))
                else:
                    instance_op.operate(input_file, output)
                output_list.append(output)
            pool.close()
            pool.join()
        inputs = output_list

        print(inputs)

