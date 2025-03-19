import { Request } from '../utils/request';
import type { CommonResponse, EmptyResponse } from '../types/responseModal';

export interface IModelConfig {
  id: number;
  provider_type: string;
  key: string;
  chat_endpoint: string;
  chat_api_key: string;
  chat_model_name: string;
  embedding_endpoint: string;
  embedding_api_key: string;
  embedding_model_name: string;
  created_at: string;
  updated_at: string;
}

export const getModelConfig = () => {
  return Request<CommonResponse<IModelConfig>>({
    method: 'get',
    url: `/api/user-llm-configs`
  });
};

export const updateModelConfig = (data: IModelConfig) => {
  return Request<CommonResponse<IModelConfig>>({
    method: 'put',
    url: `/api/user-llm-configs`,
    data
  });
};

export const deleteModelConfig = () => {
  return Request<EmptyResponse>({
    method: 'delete',
    url: `/api/user-llm-configs/key`
  });
};
