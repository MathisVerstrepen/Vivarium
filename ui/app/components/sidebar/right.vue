<script lang="ts" setup>
const route = useRoute();
const worldId = computed(() => parseInt(route.params.id as string));

const showCreateModal = ref(false);

const handleAgentCreated = () => {
    console.log('Agent created, refreshing list...');
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
                    @click="showCreateModal = true"
                    class="w-full rounded border-2 border-emerald-700 bg-emerald-800 px-4 py-3
                        font-serif font-bold text-emerald-100 shadow-lg transition-all
                        hover:bg-emerald-700 active:translate-y-0.5"
                >
                    + Create New Agent
                </button>

                <div class="mt-4 text-center font-serif text-amber-300/40 italic">
                    Agent List Coming Soon...
                </div>
            </div>
        </div>

        <AgentCreateAgentModal
            :world-id="worldId"
            :is-open="showCreateModal"
            @close="showCreateModal = false"
            @created="handleAgentCreated"
        />
    </div>
</template>
