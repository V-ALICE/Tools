import os, sys, shlex, subprocess

def batch(argv):
    if (len(argv) < 3):
        print('At least three arguments expected: batch_rule.py <defs_file> <new_working_dir> <command> [<command_args>]')
        return
        
    rule_file = argv[0].replace('\\', '/')
    wdir = argv[1].replace('\\', '/')
        
    with open(rule_file, 'r') as defs:
        def_lines = defs.readlines()
    os.chdir(wdir)   
    
    run_count, rules = define_rules(def_lines)
    if run_count == 0: return
    for x in range(run_count):
        print('Running job #'+str(x+1)+'...')
        apply_rules_and_run(rules, x, argv[2:])
    
def define_rules(lines):
    rules = {}
    run_count = 0
    for idx, line in enumerate(lines):
        segments = shlex.split(line)
        if len(segments) == 0 or line[0] == '#':
            continue
        if len(segments) < 3:
            print('Line', (idx+1), 'has too few arguments')
            continue
        if not os.path.isfile(segments[0]):
            print('Line', (idx+1), 'contains invalid path')
            continue
        if run_count > 1 and len(segments) != 3 and len(segments)-2 != run_count:
            print('Line', (idx+1), 'redefines run count')
            continue
        
        if not segments[0] in rules:
            rules[segments[0]] = []
        rules[segments[0]].append(segments[1:])
        run_count = max(run_count, len(segments)-2)
    #end for idx, line in enumerate(lines):
    
    return run_count, rules
    
def apply_rules_and_run(rules, idx, command):
    file_undo = {}
    for rule_file in rules:
        with open(rule_file, 'r') as file:
            lines = file.readlines()
            file_undo[rule_file] = lines.copy()
        
        for rule in rules[rule_file]:
            cur_rep = rule[1] if len(rule) == 2 else rule[1+idx]
            for i, line in enumerate(lines):
                lines[i] = line.replace(rule[0], cur_rep)
                
        with open(rule_file, 'w') as file:
            file.writelines(lines) 
    #end for rule in rules:
    
    try:
        subprocess.run(command, check=True, capture_output=True)
        print('\tSuccess')
    except subprocess.CalledProcessError as e:
        print('\tFailed\n')
        print(e.stdout.decode('ascii'))
    except KeyboardInterrupt:
        for filename in file_undo:
            with open(filename, 'w') as file:
                file.writelines(file_undo[filename])
        sys.exit()
        
    for filename in file_undo:
        with open(filename, 'w') as file:
            file.writelines(file_undo[filename])

if __name__ == '__main__':
    batch(sys.argv[1:])