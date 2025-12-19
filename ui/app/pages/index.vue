<script setup lang="ts">
const { fetchWorlds, createWorld } = useApi();

const { data: worlds, refresh } = await fetchWorlds();

const newWorldName = ref('');
const isCreating = ref(false);

const handleCreateWorld = async () => {
    if (!newWorldName.value) return;
    isCreating.value = true;
    try {
        await createWorld(newWorldName.value);
        newWorldName.value = '';
        refresh();
    } catch (e) {
        console.error('Failed to create world:', e);
    } finally {
        isCreating.value = false;
    }
};
</script>

<template>
    <div
        class="flex h-screen w-screen flex-col items-center justify-center bg-stone-900
            text-stone-100"
    >
        <h1 class="mb-12 font-serif text-6xl font-bold text-amber-500 drop-shadow-lg">Vivarium</h1>

        <!-- World List Container -->
        <div
            class="w-full max-w-2xl rounded-xl border-4 border-stone-700 bg-stone-800 p-8
                shadow-2xl"
        >
            <h2 class="mb-6 border-b border-stone-600 pb-2 font-serif text-2xl text-stone-300">
                Select a World
            </h2>

            <div v-if="worlds && worlds.length > 0" class="grid grid-cols-1 gap-4">
                <NuxtLink
                    v-for="world in worlds"
                    :key="world.id"
                    :to="`/world/${world.id}`"
                    class="group flex items-center justify-between rounded-lg border-2
                        border-stone-600 bg-stone-700 p-4 transition-all hover:border-amber-600
                        hover:bg-stone-600"
                >
                    <span class="text-lg font-bold text-stone-200 group-hover:text-amber-400">
                        {{ world.name }}
                    </span>
                    <span class="text-sm text-stone-400">ID: {{ world.id }}</span>
                </NuxtLink>
            </div>

            <div v-else class="py-8 text-center text-stone-500 italic">
                No worlds found. Create one to begin.
            </div>

            <!-- Create New World -->
            <div class="mt-8 border-t border-stone-600 pt-6">
                <form @submit.prevent="handleCreateWorld" class="flex gap-4">
                    <input
                        v-model="newWorldName"
                        type="text"
                        placeholder="New World Name..."
                        class="flex-1 rounded border-2 border-stone-600 bg-stone-900 px-4 py-2
                            text-white focus:border-amber-500 focus:outline-none"
                    />
                    <button
                        type="submit"
                        :disabled="isCreating || !newWorldName"
                        class="rounded bg-amber-700 px-6 py-2 font-bold text-white transition-colors
                            hover:bg-amber-600 disabled:opacity-50"
                    >
                        Create World
                    </button>
                </form>
            </div>
        </div>
    </div>
</template>
