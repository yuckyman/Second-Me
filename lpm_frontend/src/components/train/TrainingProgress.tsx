import { StageDisplayName } from '@/service/train';

interface TrainingProgressProps {
  trainingProgress: {
    overall: number;
    stage1: number;
    stage2: number;
    stage3: number;
    stage4: number;
    stage5: number;
    currentStage: string | null;
    currentStageStep: string | null;
    stageDetails?:
      | Record<
          string,
          {
            name: string;
            status: string;
            steps: Record<
              string,
              {
                name: string;
                completed: boolean;
                status: string;
              }
            >;
          }
        >
      | undefined;
  };
  status: string;
}

// Define fixed step order for each stage, must be consistent with step key names in API response
const stageStepsOrder: Record<string, string[]> = {
  stage1: ['model_download'],
  stage2: ['chunk_embedding', 'generate_document_embeddings', 'list_documents', 'process_chunks'],
  stage3: ['extract_dimensional_topics', 'map_your_entity_network'],
  stage4: ['decode_preference_patterns', 'reinforce_identity', 'augment_content_retention'],
  stage5: ['train']
};

// Get stage description
const getStageDescription = (stageKey: string) => {
  const descriptionMap: Record<string, string> = {
    stage1:
      'At this stage, we obtain the foundational model that will serve as the starting point for your Second Me. This base structure is a blank slate, ready to be shaped and enriched with your personal data, acting as the vessel that will eventually carry your unique presence.',
    stage2:
      "This step starts by processing and organizing your memories into a structured digital format that forms the groundwork for your Second Me. We break down your life experiences into smaller, meaningful pieces, encode them systematically, and extract essential insights to create a solid base. It's the first move toward building an entity that reflects your past and present.",
    stage3:
      "Here, we take the fragments of your memories and weave them into a complete, flowing biography that captures your essence. This process connects the dots between your experiences, shaping them into a coherent story that defines who you are. It's like crafting the blueprint of a new being born from your life's journey.",
    stage4:
      "To enable your Second Me to understand you fully, we create specialized training data tailored to your unique profile. This step lays the groundwork for it to grasp your preferences, identity, and knowledge accurately, ensuring the entity we're constructing can think and respond in ways that feel authentic to you.",
    stage5:
      'Finally, we train the core model with your specific memories, traits, and preferences, blending them seamlessly into its framework. This step transforms the model into a living representation of you, merging technology with your individuality to create a Second Me that feels real and true to your essence.'
  };

  return descriptionMap[stageKey] || 'Processing data...';
};

const TrainingProgress = (props: TrainingProgressProps) => {
  const { trainingProgress, status } = props;
  // Get display name for the stage
  const getStageDisplayName = (stageKey: string) => {
    // Use StageDisplayName enum as fallback
    const fallbackName = StageDisplayName[stageKey as keyof typeof StageDisplayName] || '';

    if (!trainingProgress.stageDetails) return fallbackName;

    const stageDetail =
      trainingProgress.stageDetails[stageKey as keyof typeof trainingProgress.stageDetails];

    return stageDetail.name || fallbackName;
  };

  // Get step descriptions and status for each stage
  const getStageSteps = (stageKey: string) => {
    if (!trainingProgress.stageDetails) return [];

    const stageDetail =
      trainingProgress.stageDetails[stageKey as keyof typeof trainingProgress.stageDetails];

    if (!stageDetail.steps) return [];

    // Get fixed step order for this stage
    const orderedSteps = stageStepsOrder[stageKey] || [];

    // Create step array according to fixed order
    return orderedSteps.map((stepName) => {
      const stepInfo = stageDetail.steps[stepName];

      // Special handling for model_download step
      if (
        !!stepInfo &&
        stageKey === 'stage1' &&
        stepName === 'model_download' &&
        !stepInfo.completed
      ) {
        return {
          name: stepInfo.name || stepName,
          completed: stepInfo.completed || false,
          status: 'in_progress', // Always set to in_progress unless completed
          // Always mark as current step unless completed
          isCurrent: true
        };
      }

      return {
        name: stepInfo?.name || stepName, // Use step name returned by API, or use key name if not available
        completed: stepInfo?.completed || false,
        status: stepInfo?.status || '',
        // Determine if this is the currently executing step
        isCurrent:
          trainingProgress.currentStage === stageKey &&
          trainingProgress.currentStageStep === stepName
      };
    });
  };

  // Determine stage status
  const getStageStatus = (stageKey: string) => {
    if (!trainingProgress.stageDetails) return 'pending';

    const stageDetail =
      trainingProgress.stageDetails[stageKey as keyof typeof trainingProgress.stageDetails];

    if (!stageDetail) return 'pending';

    // Special handling for stage1 (model download)
    if (stageKey === 'stage1') {
      const modelDownloadStep = stageDetail.steps.model_download;

      if (modelDownloadStep && !modelDownloadStep.completed) {
        return 'in_progress';
      }
    }

    if (stageDetail.status === 'completed') return 'completed';

    if (stageDetail.status === 'in_progress' || trainingProgress.currentStage === stageKey)
      return 'in_progress';

    return 'pending';
  };

  // Define all training stages
  const trainingStages = [
    {
      key: 'stage1',
      name: getStageDisplayName('stage1'),
      description: getStageDescription('stage1')
    },
    {
      key: 'stage2',
      name: getStageDisplayName('stage2'),
      description: getStageDescription('stage2')
    },
    {
      key: 'stage3',
      name: getStageDisplayName('stage3'),
      description: getStageDescription('stage3')
    },
    {
      key: 'stage4',
      name: getStageDisplayName('stage4'),
      description: getStageDescription('stage4')
    },
    {
      key: 'stage5',
      name: getStageDisplayName('stage5'),
      description: getStageDescription('stage5')
    }
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">
          Training Progress (may take long with more data and larger model)
        </h3>
        {(status === 'trained' || status === 'running') && (
          <span className="px-2.5 py-1 bg-green-50 text-green-700 text-sm font-medium rounded-full">
            Training Complete
          </span>
        )}
      </div>
      <div className="space-y-6">
        {/* Overall Progress */}
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-lg font-semibold text-gray-900">Overall Progress</span>
              <span className="text-2xl font-bold text-blue-600">
                {Math.round(trainingProgress.overall)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${trainingProgress.overall}%` }}
              />
            </div>
          </div>
        </div>

        {/* All Training Stages */}
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-gray-700">Training Stages</h4>
          <div className="space-y-4">
            {trainingStages.map((stage) => {
              const stageStatus = getStageStatus(stage.key);
              const progress = trainingProgress[
                stage.key as keyof typeof trainingProgress
              ] as number;

              // Handle NaN case
              const displayProgress = isNaN(progress) ? 0 : progress;

              const isCurrentStage = trainingProgress.currentStage?.replace(/-/g, '') === stage.key;
              // Get detailed information for current stage
              const stageDetail =
                trainingProgress.stageDetails?.[
                  stage.key as keyof typeof trainingProgress.stageDetails
                ];

              return (
                <div
                  key={stage.key}
                  className="bg-white rounded-lg border border-gray-100 p-4 shadow-sm"
                >
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="flex-shrink-0">
                      {stageStatus === 'completed' ? (
                        <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center">
                          <svg
                            className="w-4 h-4 text-green-600"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              d="M5 13l4 4L19 7"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth="2"
                            />
                          </svg>
                        </div>
                      ) : stageStatus === 'in_progress' ? (
                        <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center">
                          <div className="w-3 h-3 rounded-full bg-blue-600 animate-pulse" />
                        </div>
                      ) : (
                        <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center">
                          <div className="w-3 h-3 rounded-full bg-gray-300" />
                        </div>
                      )}
                    </div>

                    <div className="flex-grow">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center">
                          <span
                            className={`text-sm font-medium ${
                              isCurrentStage ? 'text-blue-700' : 'text-gray-700'
                            }`}
                          >
                            {stage.name}
                            {isCurrentStage && (
                              <span className="ml-2 text-xs text-gray-500">
                                {trainingProgress.currentStageStep &&
                                stageDetail?.steps[trainingProgress.currentStageStep]?.name
                                  ? `(${stageDetail.steps[trainingProgress.currentStageStep].name})`
                                  : `(${trainingProgress.currentStageStep})`}
                              </span>
                            )}
                          </span>
                          <button
                            className="ml-1 p-1 rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
                            onClick={() => {
                              const modal = document.createElement('div');

                              modal.className =
                                'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
                              modal.innerHTML = `
                                <div class="bg-white rounded-xl max-w-md p-6 m-4 space-y-4 relative shadow-xl">
                                  <h3 class="text-xl font-semibold">${stage.name}</h3>
                                  <div class="space-y-4 text-gray-600">
                                    <p>${stage.description}</p>
                                  </div>
                                  <button class="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600" onclick="this.parentElement.parentElement.remove()">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                  </button>
                                </div>
                              `;
                              document.body.appendChild(modal);
                              modal.onclick = (e) => {
                                if (e.target === modal) modal.remove();
                              };
                            }}
                            title="Learn more about this stage"
                          >
                            <svg
                              className="w-3 h-3"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                              />
                            </svg>
                          </button>
                        </div>
                        <span className="text-xs text-gray-500">
                          {Math.round(displayProgress)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-1.5 mt-1">
                        <div
                          className={`h-1.5 rounded-full transition-all duration-500 ${
                            stageStatus === 'completed'
                              ? 'bg-green-500'
                              : stageStatus === 'in_progress'
                                ? 'bg-blue-500'
                                : displayProgress > 0
                                  ? 'bg-blue-300'
                                  : 'bg-gray-200'
                          }`}
                          style={{ width: `${displayProgress}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Step list */}
                  <div className="mt-3 pl-9">
                    {getStageSteps(stage.key).length > 0 ? (
                      <div className="space-y-2">
                        {getStageSteps(stage.key).map((step, stepIndex) => (
                          <div key={stepIndex} className="flex items-center space-x-2">
                            <div className="flex-shrink-0">
                              {step.completed ? (
                                <div className="w-4 h-4 rounded-full bg-green-100 flex items-center justify-center">
                                  <svg
                                    className="w-3 h-3 text-green-600"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                  >
                                    <path
                                      d="M5 13l4 4L19 7"
                                      strokeLinecap="round"
                                      strokeLinejoin="round"
                                      strokeWidth="2"
                                    />
                                  </svg>
                                </div>
                              ) : step.isCurrent ? (
                                <div className="w-4 h-4 rounded-full bg-blue-100 flex items-center justify-center">
                                  <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                                </div>
                              ) : (
                                <div className="w-4 h-4 rounded-full bg-gray-100 flex items-center justify-center">
                                  <div className="w-2 h-2 rounded-full bg-gray-300" />
                                </div>
                              )}
                            </div>
                            <span
                              className={`text-xs ${
                                step.isCurrent ? 'text-blue-600 font-medium' : 'text-gray-600'
                              }`}
                            >
                              {step.name}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : stageStatus !== 'pending' ? (
                      <div className="text-xs text-gray-500">Processing...</div>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrainingProgress;
