import type {
    World,
    Agent,
    AgentDetail,
    CreateWorldRequest,
    CreateAgentRequest,
    InteractionResponse,
    WhisperRequest,
} from '~/types/vivarium';

export const useApi = () => {
    const config = useRuntimeConfig();
    const baseUrl = config.public.apiUrl;

    // --- World Operations ---

    const fetchWorlds = () => {
        return useFetch<World[]>(`${baseUrl}/worlds`, {
            key: 'worlds-list',
        });
    };

    const createWorld = async (name: string): Promise<World> => {
        return await $fetch<World>(`${baseUrl}/worlds`, {
            method: 'POST',
            body: { name } as CreateWorldRequest,
        });
    };

    // --- Agent Operations ---

    const fetchAgents = (worldId: number) => {
        return useFetch<Agent[]>(`${baseUrl}/worlds/${worldId}/agents`, {
            key: `world-${worldId}-agents`,
        });
    };

    const getAgentDetail = (agentId: number) => {
        return useFetch<AgentDetail>(`${baseUrl}/agents/${agentId}`, {
            key: `agent-${agentId}-detail`,
        });
    };

    const createAgent = async (req: CreateAgentRequest): Promise<Agent> => {
        return await $fetch<Agent>(`${baseUrl}/agents`, {
            method: 'POST',
            body: req,
        });
    };

    // --- Interaction Operations ---

    const interact = async (sourceId: number, targetId: number): Promise<InteractionResponse> => {
        return await $fetch<InteractionResponse>(`${baseUrl}/interact`, {
            method: 'POST',
            body: { source_agent_id: sourceId, target_agent_id: targetId },
        });
    };

    const whisper = async (agentId: number, content: string): Promise<void> => {
        await $fetch(`${baseUrl}/agent/whisper`, {
            method: 'POST',
            body: { agent_id: agentId, content } as WhisperRequest,
        });
    };

    return {
        fetchWorlds,
        createWorld,
        fetchAgents,
        getAgentDetail,
        createAgent,
        interact,
        whisper,
    };
};
