import { create } from 'zustand';
import type { IModelConfig } from '@/service/modelConfig';

interface ModelConfigState {
  modelConfig: IModelConfig;
  updateModelConfig: (config: IModelConfig) => void;
  deleteModelConfig: () => void;
}

export const useModelConfigStore = create<ModelConfigState>((set, get) => ({
  modelConfig: {} as IModelConfig,
  updateModelConfig(config: IModelConfig) {
    set({ modelConfig: { ...(get().modelConfig as IModelConfig), ...config } });
  },
  deleteModelConfig() {
    set({ modelConfig: {} as IModelConfig });
  }
}));
