<script setup lang="ts">
import type { MemoryItem } from '~/types/vivarium';

const props = defineProps<{
    isOpen: boolean;
    agentId: number | null;
}>();

const emit = defineEmits(['close']);

const { fetchAgentMemories } = useApi();

const isLoading = ref(false);
const agentName = ref('');
const memories = ref<MemoryItem[]>([]);
const searchQuery = ref('');
const filterCategory = ref<'ALL' | 'SELF' | 'AGENT' | 'WORLD'>('ALL');

const loadMemories = async () => {
    if (!props.agentId) return;
    isLoading.value = true;
    try {
        const data = await fetchAgentMemories(props.agentId);
        agentName.value = data.agent_name;
        memories.value = data.memories;
    } catch (e) {
        console.error('Failed to fetch memories', e);
    } finally {
        isLoading.value = false;
    }
};

watch(
    () => props.isOpen,
    (isOpen) => {
        if (isOpen) {
            loadMemories();
        } else {
            memories.value = [];
            searchQuery.value = '';
            filterCategory.value = 'ALL';
        }
    },
);

const filteredMemories = computed(() => {
    return memories.value.filter((m) => {
        const matchesSearch =
            m.content.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
            m.subject.toLowerCase().includes(searchQuery.value.toLowerCase());
        const matchesCategory =
            filterCategory.value === 'ALL' || m.category === filterCategory.value;
        return matchesSearch && matchesCategory;
    });
});

const getCategoryColor = (cat: string) => {
    switch (cat) {
        case 'SELF':
            return 'bg-purple-100 text-purple-800 border-purple-200';
        case 'AGENT':
            return 'bg-blue-100 text-blue-800 border-blue-200';
        case 'WORLD':
            return 'bg-emerald-100 text-emerald-800 border-emerald-200';
        default:
            return 'bg-stone-100 text-stone-800 border-stone-200';
    }
};
</script>

<template>
    <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
        @click.self="$emit('close')"
    >
        <div
            class="flex h-[80vh] w-200 flex-col overflow-hidden rounded-xl border-4 border-stone-700
                bg-stone-100 shadow-2xl"
        >
            <!-- Header -->
            <div
                class="flex items-center justify-between border-b-4 border-stone-700 bg-stone-800
                    px-6 py-4 text-stone-50"
            >
                <div>
                    <h2 class="font-serif text-2xl font-bold tracking-wide text-amber-500">
                        Memory Explorer
                    </h2>
                    <div class="text-sm text-stone-400">
                        Subject: <span class="font-bold text-white">{{ agentName }}</span>
                    </div>
                </div>
                <button
                    @click="$emit('close')"
                    class="rounded px-2 text-2xl font-bold text-stone-400 hover:bg-stone-700
                        hover:text-white"
                >
                    &times;
                </button>
            </div>

            <!-- Toolbar -->
            <div class="flex gap-4 border-b border-stone-300 bg-stone-200 p-4">
                <input
                    v-model="searchQuery"
                    type="text"
                    placeholder="Search memories..."
                    class="flex-1 rounded border border-stone-300 px-3 py-2 focus:border-amber-500
                        focus:outline-none"
                />
                <select
                    v-model="filterCategory"
                    class="rounded border border-stone-300 px-3 py-2 focus:border-amber-500
                        focus:outline-none"
                >
                    <option value="ALL">All Types</option>
                    <option value="SELF">Self</option>
                    <option value="AGENT">Social</option>
                    <option value="WORLD">World</option>
                </select>
                <button
                    @click="loadMemories"
                    class="rounded bg-stone-300 px-3 py-2 text-stone-700 hover:bg-stone-400"
                    title="Refresh"
                >
                    ↻
                </button>
            </div>

            <!-- List -->
            <div class="flex-1 overflow-y-auto bg-stone-100 p-6">
                <div v-if="isLoading" class="py-10 text-center text-stone-500">
                    Accessing Neural Database...
                </div>

                <div
                    v-else-if="filteredMemories.length === 0"
                    class="py-10 text-center text-stone-500 italic"
                >
                    No memories found matching criteria.
                </div>

                <div v-else class="space-y-3">
                    <div
                        v-for="mem in filteredMemories"
                        :key="mem.id"
                        class="rounded-lg border bg-white p-4 shadow-sm transition-shadow
                            hover:shadow-md"
                    >
                        <div class="mb-2 flex items-center justify-between">
                            <span
                                class="rounded-full border px-2 py-0.5 text-xs font-bold"
                                :class="getCategoryColor(mem.category)"
                            >
                                {{ mem.category }}
                            </span>
                            <span class="text-xs font-bold tracking-wider text-stone-400 uppercase">
                                {{ mem.subject }}
                            </span>
                        </div>
                        <p class="text-stone-800">{{ mem.content }}</p>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="border-t border-stone-300 bg-stone-200 px-6 py-2 text-xs text-stone-500">
                Total Memories: {{ memories.length }}
            </div>
        </div>
    </div>
</template>
