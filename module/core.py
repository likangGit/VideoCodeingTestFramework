
import os
import re
from itertools import product
import multiprocessing
from multiprocessing import cpu_count
from abc import ABC, abstractmethod
from glob import glob
class Operator(ABC):

    @abstractmethod
    def operate(input_dir, output_root):
        pass

    def extractParameters(self, filename):
        filename = os.path.basename(filename)
        searchObj = re.match(r'\D*(\d+)\D{1}(\d+)\D+(\d+\.{0,1}\d*)fps.*', filename)
        assert searchObj, 'file name is invalid:{}'.format(filename)
        w = searchObj.group(1)
        h = searchObj.group(2)
        fps = searchObj.group(3)
        return int(w), int(h), float(fps)
        
    def generateFileName(self, w, h, fps, fmt='yuv', bpp=None, avgQP=None,PSNR=None):
        filename = '{}x{}_{}fps'.format(w, h, fps)
        if bpp is not None:
            filename += '_{}bpp'.format(bpp)
        if avgQP is not None:
            filename += '_{}AvgQP'.format(avgQP)
        if PSNR is not None:
            filename += '_{}PSNR'.format(PSNR)
        filename += '.{}'.format(fmt)
        return filename

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

def inputStage(input_dir, output_dir):
    inputs = os.listdir(input_dir)
    outputs = []
    for i in inputs:
        target_path = os.path.join(output_dir, i)
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        src_file = os.path.abspath(os.path.join(input_dir, i) )
        target_file = os.path.join(target_path, i)
        if not os.path.exists(target_file):
            os.symlink(src_file,  target_file)
        outputs.append(target_file)
    return outputs

def Exec(config):
    vrStage = config.pop('visualizationResultStage')

    input_dir = config.pop('inputFolder')
    output_root = config.pop('outputFolder')
    inputs = inputStage(input_dir, output_root)
    # stage traversal
    for stageName, stageV in config.items():
        print('---------------{}-----------------'.format(stageName))

        stageKey = 'analyzerStage' if 'analyzerStage' in stageName else stageName
        assert stageKey in REGISTER, '"{}" not be registed'.format(stageName)
        stage = REGISTER[stageKey]
        assert len(inputs)>0, 'No input'
        stage_outputs = []
        # method traversal
        for methodName, methodParams in stageV.items():
            print('------{}-------'.format(methodName))
            if methodParams == 'NoParams':
                methodParams = {}
            methodParams = parseParameters(inputs, methodParams)
            methodClass = stage[methodName]['class']
            methodUseMP = stage[methodName]['useMP']
            #每个method使用线程池，不清楚线程是close是否还能再open，所以每次重新申请
            pool = multiprocessing.Pool(processes=cpu_count())
            method_outputs = []
            already_outputs = []
            for param in methodParams:
                print("parameters:",param)
                input_file = param.pop('input')
                    
                # generate output file name
                output_folder = '_'.join([stageName, methodName])+'_'
                for pk,pv in param.items():
                    output_folder += '_'.join([pk, str(pv)])+'_'
                output_folder = output_folder[:-1]

                output_path = os.path.join(os.path.dirname(input_file), output_folder)
                #TODO: if output_path already has a file, we can skip this instance
                if os.path.exists(output_path):
                    fs = os.listdir(output_path)
                    theFile = None
                    for f in fs:
                        f = os.path.join(output_path, f)
                        if os.path.isfile(f):
                            theFile = f
                            break # there is only one file in this directory.
                    if theFile:
                        already_outputs.append(theFile)
                        continue
                
                instance_op = methodClass(**param)
                if methodUseMP:
                    method_outputs.append(pool.apply_async(instance_op.operate, args=(input_file, output_path)) )
                else:
                    method_outputs.append(instance_op.operate(input_file, output_path) )
            pool.close()
            pool.join()
            if len(already_outputs) > 0:
                print('---already processed, skip these---')
                [print(item) for item in already_outputs]
            stage_outputs += [r.get() for r in method_outputs] if methodUseMP else method_outputs
            stage_outputs += already_outputs
            
        #update inputs when stage work is completed
        inputs = stage_outputs

        print('---outputs:---')
        for item in inputs:
            assert os.path.isfile(item), 'output should be a file:{}'.format(item)
            print(item)
    print('------------------visualizationResultStage---------------------')
    for methodName, methodParams  in vrStage.items():
        print('------{}------'.format(methodName))
        if 'NoParams' ==  methodParams:
            methodParams = {}
        instance = REGISTER['visualizationResultStage'][methodName]['class'](**methodParams)
        output = os.path.join(output_root, methodName)
        instance.operate(inputs, output, output_root)

