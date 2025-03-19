import { create } from 'zustand';
import type { StepStatus, StageStatus } from '@/service/train';
import { getTrainProgress, StageName } from '@/service/train';

export type ModelStatus = 'seed_identity' | 'memory_upload' | 'training' | 'trained' | 'running';

interface StageSteps {
  [key: string]: {
    completed: boolean;
    status: StepStatus;
    name: string;
  };
}

interface StageInfo {
  name: string;
  progress: number;
  status: StageStatus;
  current_step: string | null;
  steps: StageSteps;
}

interface TrainingProgress {
  overall: number;
  stage1: number;
  stage2: number;
  stage3: number;
  stage4: number;
  stage5: number;
  currentStage: StageName | null;
  currentStageStep: string | null;
  status: StageStatus;
  stageDetails: {
    stage1: StageInfo;
    stage2: StageInfo;
    stage3: StageInfo;
    stage4: StageInfo;
    stage5: StageInfo;
  };
}

interface ModelState {
  status: ModelStatus;
  error: boolean;
  isServiceStarting: boolean;
  isServiceStopping: boolean;
  trainingProgress: TrainingProgress;
  setStatus: (status: ModelStatus) => void;
  setError: (error: boolean) => void;
  setServiceStarting: (isStarting: boolean) => void;
  setServiceStopping: (isStopping: boolean) => void;
  setTrainingProgress: (progress: TrainingProgress) => void;
  checkTrainStatus: () => Promise<void>;
  resetTrainingState: () => void;
}

export const useTrainingStore = create<ModelState>((set) => ({
  status: 'seed_identity',
  isServiceStarting: false,
  isServiceStopping: false,
  error: false,
  trainingProgress: {
    overall: 0,
    stage1: 0,
    stage2: 0,
    stage3: 0,
    stage4: 0,
    stage5: 0,
    currentStage: null,
    currentStageStep: null,
    status: 'pending',
    stageDetails: {
      stage1: {
        name: 'Downloading the Base Model',
        progress: 0,
        status: 'pending',
        current_step: null,
        steps: {}
      },
      stage2: {
        name: 'Activating the Memory Matrix',
        progress: 0,
        status: 'pending',
        current_step: null,
        steps: {}
      },
      stage3: {
        name: 'Synthesize Your Life Narrative',
        progress: 0,
        status: 'pending',
        current_step: null,
        steps: {}
      },
      stage4: {
        name: 'Prepare Training Data for Deep Comprehension',
        progress: 0,
        status: 'pending',
        current_step: null,
        steps: {}
      },
      stage5: {
        name: 'Training to create Second Me',
        progress: 0,
        status: 'pending',
        current_step: null,
        steps: {}
      }
    }
  },
  setStatus: (status) => set({ status }),
  setError: (error) => set({ error }),
  setServiceStarting: (isStarting) => set({ isServiceStarting: isStarting }),
  setServiceStopping: (isStopping) => set({ isServiceStopping: isStopping }),
  setTrainingProgress: (progress) => set({ trainingProgress: progress }),
  resetTrainingState: () =>
    set({
      status: 'memory_upload',
      error: false,
      trainingProgress: {
        overall: 0,
        stage1: 0,
        stage2: 0,
        stage3: 0,
        stage4: 0,
        stage5: 0,
        currentStage: StageName.Stage1,
        currentStageStep: 'model_download',
        status: 'in_progress',
        stageDetails: {
          stage1: {
            name: 'Downloading the Base Model',
            progress: 0,
            status: 'in_progress',
            current_step: 'model_download',
            steps: {
              model_download: {
                completed: false,
                status: 'in_progress',
                name: 'Downloading the Base Model'
              }
            }
          },
          stage2: {
            name: 'Activating the Memory Matrix',
            progress: 0,
            status: 'pending',
            current_step: null,
            steps: {}
          },
          stage3: {
            name: 'Synthesize Your Life Narrative',
            progress: 0,
            status: 'pending',
            current_step: null,
            steps: {}
          },
          stage4: {
            name: 'Prepare Training Data for Deep Comprehension',
            progress: 0,
            status: 'pending',
            current_step: null,
            steps: {}
          },
          stage5: {
            name: 'Training to create Second Me',
            progress: 0,
            status: 'pending',
            current_step: null,
            steps: {}
          }
        }
      }
    }),
  checkTrainStatus: async () => {
    const config = JSON.parse(localStorage.getItem('trainingConfig') || '{}');

    set({ error: false });

    try {
      const res = await getTrainProgress({
        model_name: config.baseModel || 'Qwen2.5-0.5B-Instruct'
      });

      if (res.data.code === 0) {
        const data = res.data.data;
        const { stages, overall_progress, current_stage, status } = data;

        const newProgress = {
          overall: overall_progress,
          stage1: stages.downloading_the_base_model.progress,
          stage2: stages.activating_the_memory_matrix.progress,
          stage3: stages.synthesize_your_life_narrative.progress,
          stage4: stages.prepare_training_data_for_deep_comprehension.progress,
          stage5: stages.training_to_create_second_me.progress,
          currentStage: current_stage as StageName,
          currentStageStep: current_stage ? stages[current_stage].current_step : null,
          status: status,
          stageDetails: {
            stage1: stages.downloading_the_base_model,
            stage2: stages.activating_the_memory_matrix,
            stage3: stages.synthesize_your_life_narrative,
            stage4: stages.prepare_training_data_for_deep_comprehension,
            stage5: stages.training_to_create_second_me
          }
        };

        if (newProgress.status === 'failed') {
          set({ error: true });
        }

        set((state) => {
          // If current status is running, keep it unchanged
          if (state.status === 'running') {
            return {
              ...state,
              trainingProgress: newProgress
            };
          }

          const newState = {
            ...state,
            trainingProgress: newProgress
          };

          // If total progress is 100%, set status to trained
          if (overall_progress === 100) {
            newState.status = 'trained';
          }
          // If there's any progress but not complete, set status to training
          else if (overall_progress > 0) {
            newState.status = 'training';
          }

          return newState;
        });
      }
    } catch (error) {
      console.error('Error checking training status:', error);
      set({ error: true });
    }
  }
}));
