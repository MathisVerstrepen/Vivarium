import type {
    World,
    Agent,
    AgentDetail,
    CreateWorldRequest,
    CreateAgentRequest,
    InteractionResponse,
    WhisperRequest,
    AgentProfile,
    ChatResponse,
    EndChatResponse,
    MemoryExplorerResponse,
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

    // Reactive fetch for component setup
    const getAgentDetail = (agentId: number) => {
        return useFetch<AgentDetail>(`${baseUrl}/agents/${agentId}`, {
            key: `agent-${agentId}-detail`,
        });
    };

    // Imperative fetch for event handlers (e.g., clicking Edit)
    const fetchAgentDetailRaw = async (agentId: number): Promise<AgentDetail> => {
        return await $fetch<AgentDetail>(`${baseUrl}/agents/${agentId}`);
    };

    const createAgent = async (req: CreateAgentRequest): Promise<Agent> => {
        return await $fetch<Agent>(`${baseUrl}/agents`, {
            method: 'POST',
            body: req,
        });
    };

    const updateAgent = async (agentId: number, profile: AgentProfile): Promise<AgentDetail> => {
        return await $fetch<AgentDetail>(`${baseUrl}/agents/${agentId}`, {
            method: 'PUT',
            body: profile,
        });
    };

    const deleteAgent = async (agentId: number): Promise<void> => {
        await $fetch(`${baseUrl}/agents/${agentId}`, {
            method: 'DELETE',
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

    const chatWithAgent = async (agentId: number, message: string): Promise<ChatResponse> => {
        return await $fetch<ChatResponse>(`${baseUrl}/agent/chat`, {
            method: 'POST',
            body: { agent_id: agentId, message },
        });
    };

    const endChat = async (agentId: number): Promise<EndChatResponse> => {
        return await $fetch<EndChatResponse>(`${baseUrl}/agent/chat/end`, {
            method: 'POST',
            body: { agent_id: agentId },
        });
    };

    // --- Debug / Explorer ---

    const fetchAgentMemories = async (agentId: number): Promise<MemoryExplorerResponse> => {
        return await $fetch<MemoryExplorerResponse>(`${baseUrl}/agents/${agentId}/memories`);
    };

    return {
        fetchWorlds,
        createWorld,
        fetchAgents,
        getAgentDetail,
        fetchAgentDetailRaw,
        createAgent,
        updateAgent,
        deleteAgent,
        interact,
        whisper,
        chatWithAgent,
        endChat,
        fetchAgentMemories,
    };
};
