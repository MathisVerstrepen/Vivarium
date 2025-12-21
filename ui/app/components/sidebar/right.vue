<script lang="ts" setup>
import type { AgentDetail } from '~/types/vivarium';

const route = useRoute();
const worldId = computed(() => parseInt(route.params.id as string));

const { fetchAgents, fetchAgentDetailRaw, deleteAgent } = useApi();

const { data: agents, refresh } = await fetchAgents(worldId.value);

const showModal = ref(false);
const selectedAgent = ref<AgentDetail | null>(null);

// Open modal for Creation
const openCreateModal = () => {
    selectedAgent.value = null;
    showModal.value = true;
};

// Open modal for Editing
const openEditModal = async (agentId: number) => {
    try {
        const detail = await fetchAgentDetailRaw(agentId);
        selectedAgent.value = detail;
        showModal.value = true;
    } catch (e) {
        console.error('Failed to fetch agent details', e);
    }
};

const handleDelete = async (agentId: number) => {
    if (confirm('Are you sure you want to delete this agent? This cannot be undone.')) {
        try {
            await deleteAgent(agentId);
            refresh();
        } catch (e) {
            console.error('Failed to delete agent', e);
        }
    }
};

const handleModalSuccess = () => {
    refresh();
};
</script>

<template>
    <div
        class="pointer-events-auto absolute top-4 right-4 z-40 h-[calc(100vh-2rem)] w-96 rounded-lg
            border-4 border-amber-800 bg-amber-900 p-1 shadow-2xl shadow-black"
    >
        <div class="flex h-full flex-col rounded border-2 border-amber-700/50 bg-amber-900 p-4">
            <h2
                class="mb-6 border-b-2 border-amber-800 pb-2 text-center font-serif text-2xl
                    font-bold text-amber-100 drop-shadow-md"
            >
                God Mode
            </h2>

            <div class="flex flex-col gap-4">
                <button
                    @click="openCreateModal"
                    class="w-full rounded border-2 border-emerald-700 bg-emerald-800 px-4 py-3
                        font-serif font-bold text-emerald-100 shadow-lg transition-all
                        hover:bg-emerald-700 active:translate-y-0.5"
                >
                    + Create New Agent
                </button>

                <div class="mt-4 flex-1 overflow-y-auto">
                    <h3 class="mb-2 font-serif font-bold text-amber-200">Population</h3>

                    <div v-if="agents && agents.length > 0" class="flex flex-col gap-2">
                        <div
                            v-for="agent in agents"
                            :key="agent.id"
                            class="group relative flex flex-col gap-1 rounded border
                                border-amber-700 bg-amber-800/50 p-3 pr-10 transition-colors
                                hover:bg-amber-800"
                        >
                            <div class="font-bold text-amber-100">{{ agent.name }}</div>
                            <div class="truncate text-xs text-amber-300/60">
                                {{ agent.current_situation }}
                            </div>

                            <!-- Action Buttons -->
                            <div
                                class="absolute top-2 right-2 flex gap-1 opacity-0
                                    transition-opacity group-hover:opacity-100"
                            >
                                <button
                                    @click.stop="openEditModal(agent.id)"
                                    class="rounded bg-amber-700 p-1 text-amber-100
                                        hover:bg-amber-600"
                                    title="Edit Personality"
                                >
                                    <Icon name="lucide:edit" class="h-4 w-4" />
                                </button>
                                <button
                                    @click.stop="handleDelete(agent.id)"
                                    class="rounded bg-red-900/80 p-1 text-red-200 hover:bg-red-700"
                                    title="Delete Agent"
                                >
                                    <Icon name="lucide:trash-2" class="h-4 w-4" />
                                </button>
                            </div>
                        </div>
                    </div>

                    <div v-else class="text-center font-serif text-amber-300/40 italic">
                        No agents in this world yet.
                    </div>
                </div>
            </div>
        </div>

        <AgentCreateAgentModal
            :world-id="worldId"
            :is-open="showModal"
            :agent-to-edit="selectedAgent"
            @close="showModal = false"
            @created="handleModalSuccess"
            @updated="handleModalSuccess"
        />
    </div>
</template>
