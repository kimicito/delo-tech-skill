#!/usr/bin/env python3
"""AI Pipeline — State Machine Executor

Выполняет pipeline шаг за шагом: checkpoint, retry, error handling.
"""

import json
import argparse
import sys
import time
from datetime import datetime
from pathlib import Path


def load_config(config_path):
    with open(config_path, encoding='utf-8') as f:
        return json.load(f)


def find_pipeline(config, pipeline_id):
    for p in config['pipelines']:
        if p['id'] == pipeline_id:
            return p
    raise ValueError(f"Pipeline '{pipeline_id}' not found")


def load_state(pipeline_id):
    """Загружает последний checkpoint."""
    state_dir = Path('state')
    if not state_dir.exists():
        return None
    
    files = sorted(state_dir.glob(f'{pipeline_id}_*.json'), reverse=True)
    if files:
        with open(files[0], encoding='utf-8') as f:
            return json.load(f)
    return None


def save_state(pipeline_id, step_idx, outputs, errors):
    """Сохраняет checkpoint."""
    state_dir = Path('state')
    state_dir.mkdir(exist_ok=True)
    
    state = {
        'pipeline_id': pipeline_id,
        'timestamp': datetime.now().isoformat(),
        'current_step': step_idx,
        'outputs': outputs,
        'errors': errors
    }
    
    path = state_dir / f"{pipeline_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    return path


def execute_step(step, inputs, outputs):
    """Выполняет один шаг (stub — реальная интеграция с OpenClaw skills)."""
    print(f"  [Step {step['id']}] {step['name']}...")
    
    # Здесь будет реальная интеграция:
    # - Вызов skill через OpenClaw
    # - Обработка input (template substitution)
    # - Сохранение output
    
    time.sleep(1)  # Симуляция работы
    
    # Stub result
    result = {
        'step_id': step['id'],
        'status': 'success',
        'output': f"/output/{step['id']}_{datetime.now().strftime('%Y%m%d')}.tmp"
    }
    
    print(f"  ✓ {step['name']} completed")
    return result


def run_pipeline(pipeline, user_input, resume=False):
    """Главный цикл pipeline."""
    pipeline_id = pipeline['id']
    steps = pipeline['steps']
    
    # Load or init state
    state = load_state(pipeline_id) if resume else None
    if state:
        start_step = state['current_step']
        outputs = state['outputs']
        errors = state['errors']
        print(f"Resuming from step {start_step} (checkpoint)")
    else:
        start_step = 0
        outputs = {}
        errors = []
    
    print(f"\nPipeline: {pipeline['name']}")
    print(f"Steps: {len(steps)}")
    print(f"Input: {user_input}")
    print("=" * 40)
    
    for i, step in enumerate(steps):
        if i < start_step:
            print(f"  [Step {step['id']}] Skipped (already done)")
            continue
        
        # Retry loop
        max_retries = step.get('retry', 3)
        for attempt in range(max_retries + 1):
            try:
                result = execute_step(step, user_input, outputs)
                outputs[step['id']] = result['output']
                break
            except Exception as e:
                errors.append({'step': step['id'], 'error': str(e), 'attempt': attempt})
                if attempt < max_retries:
                    wait = 30 * (attempt + 1)
                    print(f"  ⚠ Retry {attempt+1}/{max_retries} in {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"  ✗ Step {step['id']} failed after {max_retries} retries")
                    save_state(pipeline_id, i, outputs, errors)
                    return {'status': 'failed', 'step': i, 'errors': errors}
        
        # Save checkpoint after each successful step
        save_state(pipeline_id, i + 1, outputs, errors)
    
    print("=" * 40)
    print(f"✅ Pipeline completed: {pipeline_id}")
    print(f"📁 Outputs: {len(outputs)}")
    
    return {'status': 'completed', 'outputs': outputs}


def main():
    parser = argparse.ArgumentParser(description='AI Pipeline Executor')
    parser.add_argument('--config', '-c', default='config/pipelines.json', help='Pipelines config')
    parser.add_argument('--pipeline', '-p', required=True, help='Pipeline ID')
    parser.add_argument('--input', '-i', required=True, help='Input data/topic')
    parser.add_argument('--resume', '-r', action='store_true', help='Resume from checkpoint')
    args = parser.parse_args()
    
    config = load_config(args.config)
    pipeline = find_pipeline(config, args.pipeline)
    
    result = run_pipeline(pipeline, args.input, resume=args.resume)
    
    if result['status'] == 'failed':
        print(f"\n❌ Pipeline failed at step {result['step']}")
        for e in result['errors']:
            print(f"   - {e['step']}: {e['error']}")
        sys.exit(1)
    
    print(f"\n📊 Summary:")
    for k, v in result['outputs'].items():
        print(f"   {k}: {v}")


if __name__ == '__main__':
    main()
