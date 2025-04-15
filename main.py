import time
import tqdm
import os
import json
import importlib
import pkgutil

from random import seed as set_seed

import dsl
from dsl import *

import utils
from utils import *

import generators
# import verifiers


def get_functions_from_pkg(pkg_path: str, prefix: str) -> dict:
    """
    Dynamically loads functions starting with a specific prefix from all modules
    within a given package path.
    """
    functions_map = {}
    try:
        pkg = importlib.import_module(pkg_path.replace('/', '.'))
        package_path = pkg.__path__
        package_name = pkg.__name__
    except ImportError as e:
        print(f"Warning: Could not import package {pkg_path}. Error: {e}")
        return functions_map # Return empty if base package doesn't exist

    for _, module_name, _ in pkgutil.walk_packages(package_path, prefix=package_name + '.'):
        try:
            module = importlib.import_module(module_name)
            for attribute_name in dir(module):
                if attribute_name.startswith(prefix):
                    attribute = getattr(module, attribute_name)
                    if callable(attribute):
                        key = strip_prefix(attribute_name, prefix)
                        if key in functions_map:
                            print(f"Warning: Duplicate function key '{key}' found in {module_name}. Overwriting.")
                        functions_map[key] = attribute
        except Exception as e:
            print(f"Warning: Could not import or process module {module_name}. Error: {e}")
            
    return functions_map


def get_generators() -> dict:
    """
    returns mapper from task identifiers (keys) to example generator functions
    Loads from all submodules within the 'generators' package.
    """
    return get_functions_from_pkg('generators', 'generate_')


def get_verifiers() -> dict:
    """
    returns mapper from task identifiers (keys) to example verifier functions
    Loads from all submodules within the 'verifiers' package.
    """
    return get_functions_from_pkg('verifiers', 'verify_')


def get_rng_difficulty(
    example: dict
) -> float:
    """
    RNG-Difficulty: proxy measure for example difficulty, defined as the mean of sampled floats within example generation
    """
    rng = getattr(utils, 'rng')
    setattr(utils, 'rng', [])
    return sum(rng) / len(rng)


def get_pso_difficulty(
    example: dict
) -> float:
    """
    PSO-Difficulty: proxy measure for example difficulty, defined as weighted sum of #Pixels, #Symbols, #Objects
    """
    i, o = example['input'], example['output']
    hwi = height(i) * width(i)
    hwo = height(o) * width(o)
    pix_pct = (hwi + hwo) / 1800
    col_pct = len(palette(i) | palette(o)) / 10
    obj_dens = (len(objects(i, T, F, F)) / hwi + len(objects(o, T, F, F)) / hwo) / 2
    return (pix_pct + col_pct + obj_dens) / 3


def demo_generator(key, n=6):
    with open(f'arc_original/training/{key}.json', 'r') as fp:
        original_task = json.load(fp)
    original_task = original_task['train'] + original_task['test']
    generator = getattr(generators, f'generate_{key}')
    generated_examples = [generator(0, 1) for k in range(n)]
    plot_task(original_task)
    plot_task(generated_examples)
    

def generate_dataset(
    path: str = 're_arc',
    seed: int = 42,
    n_examples: int = 1000,
    diff_lb: float = 0,
    diff_ub: float = 1
) -> None:
    """
    generates dataset

    path: which folder to save data to
    seed: for deterministic generation / reproducibility
    n_examples: number of examples per task
    diff_lb: lower bound for difficulty
    diff_ub: upper bound for difficulty
    """
    set_seed(seed)
    os.makedirs(path)
    tasks_path = os.path.join(path, 'tasks')
    os.makedirs(tasks_path)
    generators_mapper = get_generators()
    verifiers_mapper = get_verifiers()
    keys = sorted(generators_mapper.keys())
    k = len(keys)
    desc = f'task 0/{k}, example 0/{n_examples}'
    pbar = tqdm.tqdm(enumerate(keys), desc=desc, position=0, leave=True, total=k)
    metadata = dict()
    for i, key in pbar:
        generator = generators_mapper[key]
        verifier = verifiers_mapper[key]
        seen = set()
        examples = []
        stats = {
            'n_generations': 0, 'n_verified': 0, 'n_nondegenerate': 0,
            'rng_difficulties': [], 'pso_difficulties': []
        }
        start = time.time()
        while len(examples) < n_examples:
            example, identifier, success = None, None, True
            try:
                example = generator(diff_lb, diff_ub)
                assert is_grid(example['input'])
                assert is_grid(example['output'])
                identifier = hash(example['input'])
                stats['n_generations'] += 1
            except:
                success = False
            try:
                assert success and verifier(example['input']) == example['output']
                stats['n_verified'] += 1
            except:
                success = False
            try:
                assert success and example['input'] != example['output']
                stats['n_nondegenerate'] += 1
            except:
                success = False
            if success and identifier not in seen:
                examples.append(example)
                seen.add(identifier)
                stats['rng_difficulties'].append(get_rng_difficulty(example))
                stats['pso_difficulties'].append(get_pso_difficulty(example))
                desc = f'task {i+1}/{k}, example {len(examples)}/{n_examples}'
                pbar.set_description(desc)
        end = time.time()
        stats['runtime'] = end - start
        with open(os.path.join(tasks_path, f'{key}.json'), 'w') as fp:
            json.dump(examples, fp)
        metadata[key] = stats
    with open(os.path.join(path, 'metadata.json'), 'w') as fp:
        json.dump(metadata, fp)


def demo_dataset(
    folder: str = 're_arc',
    n: int = 8,
    s: int = 0,
    e: int = 400
) -> None:
    """
    visualizing snippets from a generated dataset (original, easy, medium and hard instances for each task)
    """
    with open(f'{folder}/metadata.json', 'r') as fp:
        metadata = json.load(fp)
    for i, fn in enumerate(sorted(os.listdir(f'{folder}/tasks'))):
        if s <= i < e:
            key = fn[:8]
            with open(f'arc_original/training/{key}.json', 'r') as fp:
                original_task = json.load(fp)
            with open(f'{folder}/tasks/{key}.json', 'r') as fp:
                generated_task = json.load(fp)
            original_task = [format_example(example) for example in original_task['train'] + original_task['test']]
            generated_task = [format_example(example) for example in generated_task[:10*n]]
            difficulties = metadata[key]['pso_difficulties'][:9*n]
            generated_task = [ex for ex, diff in sorted(zip(generated_task, difficulties), key=lambda item: item[1])]
            easy = generated_task[1*n:2*n]
            hard = generated_task[8*n:9*n]
            print(key)
            print('original:')
            plot_task(original_task)
            print('generated (easy):')
            plot_task(easy)
            print('generated (hard):')
            plot_task(hard)


def evaluate_verifiers_on_original_tasks() -> None:
    """
    runs the verifiers on the original ARC training tasks
    """
    verifiers = get_verifiers()
    dataset = dict()
    for key in verifiers.keys():
        with open(f'arc_original/training/{key}.json', 'r') as fp:
            task = json.load(fp)
        dataset[key] = format_task(task)
    fix_bugs(dataset)
    failed_on = set()
    for key, verifier in verifiers.items():
        task = dataset[key]
        try:
            for example in task['train'] + task['test']:
                assert verifier(example['input']) == example['output']
        except:
            failed_on.add(key)
    n = len(dataset)
    k = len(failed_on)
    print(f'verification programs work for all examples for {n-k}/{n} tasks')
    print(f'verification fails (on one example) for tasks {failed_on}')


def generate_single_task(
    key: str,
    num_examples: int = 5,
    diff_lb: float = 0,
    diff_ub: float = 1,
    seed_val: int = 42
) -> list:
    """
    Generate examples for a single task specified by key.
    
    Parameters:
    -----------
    key : str
        The identifier of the task (should match a generator function)
    num_examples : int, default=5
        Number of examples to generate
    diff_lb : float, default=0
        Lower bound for difficulty
    diff_ub : float, default=1
        Upper bound for difficulty
    seed_val : int, default=42
        Random seed for reproducibility
    
    Returns:
    --------
    list
        List of generated examples
    """
    set_seed(seed_val)
    print(f"{seed_val=}")
    generators_mapper = get_generators()
    verifiers_mapper = get_verifiers()
    
    if key not in generators_mapper:
        raise ValueError(f"No generator found for key: {key}")
    
    generator = generators_mapper[key]
    verifier = verifiers_mapper.get(key)
    
    examples = []
    seen = set()
    stats = {
        'n_generations': 0, 'n_verified': 0, 'n_nondegenerate': 0
    }
    
    while len(examples) < num_examples:
        example, identifier, success = None, None, True
        # try:
        example = generator(diff_lb, diff_ub)
        assert is_grid(example['input']) or is_line(example['input'])
        assert is_grid(example['output']) or is_line(example['output'])
        identifier = hash(example['input'])
        stats['n_generations'] += 1
        # except Exception as e:
        #     raise Exception(f"Error generating example: {e}")
        #     success = False
        # try:
        #     assert success and verifier(example['input']) == example['output']
        #     stats['n_verified'] += 1
        # except:
        #     success = False
        # try:
        #     assert success and example['input'] != example['output']
        #     stats['n_nondegenerate'] += 1
        # except:
        #     success = False
        
        if success and identifier not in seen:
            examples.append(example)
            seen.add(identifier)
            print(f"Generated example {len(examples)}/{num_examples}")
    
    return examples


def verify_single_task(
    key: str,
    examples: list = None
) -> bool:
    """
    Verify examples for a task using its verifier.
    If examples are not provided, uses original ARC training examples.
    
    Parameters:
    -----------
    key : str
        The identifier of the task
    examples : list, optional
        List of examples to verify. If None, uses original examples
    
    Returns:
    --------
    bool
        True if all examples pass verification, False otherwise
    """
    verifiers_mapper = get_verifiers()
    
    if key not in verifiers_mapper:
        raise ValueError(f"No verifier found for key: {key}")
    
    verifier = verifiers_mapper[key]
    
    if examples is None:
        # Use original examples if none provided
        try:
            with open(f'arc_original/training/{key}.json', 'r') as fp:
                task = json.load(fp)
            examples = task['train'] + task['test']
        except Exception as e:
            print(f"Error loading original examples: {e}")
            return False
    
    all_correct = True
    for i, example in enumerate(examples):
        try:
            verified_output = verifier(example['input'])
            if verified_output == example['output']:
                print(f"Example {i+1}: Verification passed")
            else:
                print(f"Example {i+1}: Verification failed - outputs don't match")
                all_correct = False
        except Exception as e:
            print(f"Example {i+1}: Verification error")
            all_correct = False
    
    return all_correct


def test_single_task(
    key: str,
    num_examples: int = 5,
    diff_lb: float = 0,
    diff_ub: float = 1,
    seed_val: int = 42
) -> list:
    """
    Generate and verify examples for a single task, with visualization.
    
    Parameters:
    -----------
    key : str
        The identifier of the task
    num_examples : int, default=5
        Number of examples to generate
    diff_lb : float, default=0
        Lower bound for difficulty
    diff_ub : float, default=1
        Upper bound for difficulty
    seed_val : int, default=42
        Random seed for reproducibility
        
    Returns:
    --------
    list
        List of generated examples
    """
    print(f"Testing task: {key}")
    examples = generate_single_task(key, num_examples, diff_lb, diff_ub, seed_val)
    
    print("\nVerifying examples:")
    verify_single_task(key, examples)
    
    print("\nPlotting examples:")
    plot_task(examples)
    
    return examples


def compare_with_original(
    key: str,
    generated_examples: list = None,
    num_examples: int = 5, 
    diff_lb: float = 0,
    diff_ub: float = 1,
    seed_val: int = 42
) -> None:
    """
    Compare generated examples with original examples from the ARC dataset.
    
    Parameters:
    -----------
    key : str
        The identifier of the task
    generated_examples : list, default=None
        List of generated examples, if None, examples will be generated
    num_examples : int, default=5
        Number of examples to generate if generated_examples is None
    diff_lb : float, default=0
        Lower bound for difficulty
    diff_ub : float, default=1
        Upper bound for difficulty
    seed_val : int, default=42
        Random seed for reproducibility
        
    Returns:
    --------
    None
    """
    try:
        with open(f'arc_original/training/{key}.json', 'r') as fp:
            original_task = json.load(fp)
        original_examples = original_task['train'] + original_task['test']
        print(f"Found {len(original_examples)} original examples")
    except Exception as e:
        print(f"Error loading original examples: {e}")
        original_examples = []
    
    if not generated_examples:
        generated_examples = generate_single_task(key, num_examples, diff_lb, diff_ub, seed_val)
    
    print("\nOriginal examples:")
    if original_examples:
        plot_task(original_examples)
    else:
        print("No original examples available")
        
    print("\nGenerated examples:")
    if generated_examples:
        plot_task(generated_examples)
    else:
        print("No generated examples available")


def plot_task_key(
    key: str,
    arc_version: int = None,
    subset: str = None,
    show_train: bool = True,
    show_test: bool = True
) -> None:
    """
    Plot examples from a task, searching across datasets/subsets if needed.
    
    Parameters:
    -----------
    key : str
        The identifier of the task to plot
    arc_version : int, optional
        Version of the ARC dataset (1 for arc_original, 2 for arc2). 
        If None, searches both.
    subset : str, optional
        Dataset subset ("training" or "evaluation"). 
        If None, searches both.
    show_train : bool, default=True
        Whether to include training examples
    show_test : bool, default=True
        Whether to include test examples
        
    Returns:
    --------
    None
    """
    possible_paths = []
    if arc_version is not None and subset is not None:
        # If specific version and subset are given, use that path directly
        dataset_path = "arc_original" if arc_version == 1 else "arc2"
        possible_paths.append(f'{dataset_path}/{subset}/{key}.json')
    else:
        versions_to_check = [1, 2] if arc_version is None else [arc_version]
        subsets_to_check = ["training", "evaluation"] if subset is None else [subset]
        for v in versions_to_check:
            dataset_path = "arc_original" if v == 1 else "arc2"
            for s in subsets_to_check:
                 possible_paths.append(f'{dataset_path}/{s}/{key}.json')

    task_found = False
    for file_path in possible_paths:
        try:
            # Attempt to open and process the file
            with open(file_path, 'r') as fp:
                task = json.load(fp)
            
            print(f"Found task '{key}' at: {file_path}")
            task = format_task(task)
            examples_to_plot = []
            if show_train and 'train' in task:
                examples_to_plot.extend(task['train'])
            if show_test and 'test' in task:
                examples_to_plot.extend(task['test'])
                
            if not examples_to_plot:
                print(f"No examples found to plot for task '{key}'")
            else:
                task_found = True
                plot_task(examples_to_plot)
            
            # break # Stop searching once found

        except FileNotFoundError:
            # If file not found, continue to the next possible path
            continue 
        except Exception as e:
            # Handle other potential errors during file loading/processing
            print(f"Error processing task file {file_path}: {e}")
            # Optionally break or return depending on desired error handling
            # break 

    if not task_found:
        print(f"Error: Task '{key}' not found in the specified locations.")


def list_tasks(
    arc_version: int = 1,
    subset: str = "evaluation",
    n: int = None
) -> list:
    """
    List available tasks from either arc_original or arc2 dataset.
    
    Parameters:
    -----------
    arc_version : int, default=1
        Version of the ARC dataset (1 for arc_original, 2 for arc2)
    subset : str, default="evaluation"
        Dataset subset ("training" or "evaluation")
    n : int, optional
        If provided, only list the first n tasks
        
    Returns:
    --------
    list
        List of task keys
    """
    dataset_path = "arc_original" if arc_version == 1 else "arc2"
    
    try:
        folder_path = f'{dataset_path}/{subset}'
        tasks = sorted([f.split('.')[0] for f in os.listdir(folder_path) if f.endswith('.json')])
        if n is not None:
            tasks = tasks[:n]
        
        for i, task in enumerate(tasks):
            print(f"{i+1}. {task}")
            
        return tasks
    except Exception as e:
        print(f"Error listing tasks: {e}")
        return []


def explore_tasks(
    arc_version: int = 1,
    subset: str = "evaluation",
    start_idx: int = 0,
    num_tasks: int = 5
) -> None:
    """
    Interactive function to explore multiple tasks sequentially from either arc_original or arc2.
    
    Parameters:
    -----------
    arc_version : int, default=1
        Version of the ARC dataset (1 for arc_original, 2 for arc2)
    subset : str, default="evaluation"
        Dataset subset ("training" or "evaluation")
    start_idx : int, default=0
        Index to start from in the sorted list of tasks
    num_tasks : int, default=5
        Number of tasks to display
        
    Returns:
    --------
    None
    """
    dataset_path = "arc_original" if arc_version == 1 else "arc2"
    dataset_name = "ARC-AGI-1" if arc_version == 1 else "ARC-AGI-2"
    
    try:
        folder_path = f'{dataset_path}/{subset}'
        tasks = sorted([f.split('.')[0] for f in os.listdir(folder_path) if f.endswith('.json')])
        end_idx = min(start_idx + num_tasks, len(tasks))
        
        print(f"\nExploring {dataset_name} {subset} tasks ({start_idx+1}-{end_idx} of {len(tasks)} total tasks)")
        
        for i, task_key in enumerate(tasks[start_idx:end_idx]):
            print(f"\nTask {start_idx + i + 1}/{len(tasks)}: {task_key}")
            plot_task_key(task_key, arc_version, subset)
            
    except Exception as e:
        print(f"Error exploring tasks: {e}")
