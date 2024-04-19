import os
import shutil
import subprocess
import filecmp
import sys
import time
import psutil

def measure_ram():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss  # in bytes


def run_and_measure(cmd):
    start_time = time.time()
    start_ram = measure_ram()

    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, shell=True, check=True)

    end_ram = measure_ram()
    end_time = time.time()

    execution_time = end_time - start_time
    ram_usage = (end_ram - start_ram) / 1000000
    print(f"Time: {execution_time:<15.3f}s RAM: {ram_usage:<15} MB")

    return result, execution_time, ram_usage

def compile_and_run_cpp(input_dir, output_dir, cpp_file):
    # Compile C++ file
    compile_command = f"clang++ -o {cpp_file.split('.')[0]} --std=c++14 {cpp_file}"
    subprocess.run(compile_command, shell=True, check=True)

    # Get list of input files
    input_files = [file for file in os.listdir(input_dir) if file.endswith('.in')]

    localInputFile = "server.in"

    # Execute C++ executable for each input file
    for testInputFile in input_files:
        print(f"\nTesting {testInputFile}")
        # Copy input file to current directory
        shutil.copy(os.path.join(input_dir, testInputFile), localInputFile)
        
        # Execute C++ executable with input file
        executable = cpp_file.split('.')[0]
        run_and_measure(f"./{executable}", )
        # res, time, ram = run_and_measure("./{executable}")
        # print(f"Time: {time:<15} RAM: {ram:<15}")
        # Compare output with existing output file if it exists
        expectedOutputFile = os.path.join(output_dir, testInputFile.replace('.in', '.out'))
        
        testSuccessful = True
        if os.path.exists(expectedOutputFile):
            actualOutputFile = open("server.out", "r")
            expectedOutputFile = open(expectedOutputFile)
            for line_num, (actualLine, expectedLine) in enumerate(zip(actualOutputFile, expectedOutputFile), start=1):
                if actualLine.strip() != expectedLine.strip():
                    print("Different output: ")
                    print(f"Actual:   {actualLine.strip()}")
                    print(f"Expected: {expectedLine.strip()}")
                    testSuccessful = False
                    break
                    # return line_num, actualLine.strip(), expectedLine.strip()
            # if filecmp.cmp(f"server.out", expectedOutputFile):
            #     print(f"Output for {input_file} matches {expectedOutputFile}")
            # else:
            #     print(f"Output for {input_file} does not match {expectedOutputFile}")
        else:
            print(f"No output file found for {testInputFile}")

        if testSuccessful:
            print("Test OK")
        else:
            print("Test FAILED")
        # Remove copied input file
        os.remove(localInputFile)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_directory> <output_directory> <cpp_file>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    cpp_filename = sys.argv[3]
    compile_and_run_cpp(input_directory, output_directory, cpp_filename)
