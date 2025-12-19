<script setup lang="ts">
const route = useRoute();
const worldId = route.params.id;
</script>

<template>
    <div
        class="relative flex h-screen w-screen items-center justify-center overflow-hidden bg-black"
    >
        <!-- Game Layer -->
        <ClientOnly>
            <PhaserInstance :world-id="parseInt(worldId as string)" />
            <template #fallback>
                <div class="text-white">Loading Simulation...</div>
            </template>
        </ClientOnly>

        <!-- UI Overlay Layer -->
        <div class="pointer-events-none absolute inset-0 z-10">
            <div class="pointer-events-auto">
                <SidebarLeft />
            </div>
            <div class="pointer-events-auto">
                <SidebarRight />
            </div>
        </div>

        <!-- Back Button -->
        <NuxtLink
            to="/"
            class="absolute top-4 left-1/2 z-50 -translate-x-1/2 rounded-full border
                border-stone-600 bg-stone-800/50 px-4 py-1 text-xs text-stone-400 backdrop-blur-lg
                hover:bg-stone-700/80 hover:text-white"
        >
            Exit World
        </NuxtLink>
    </div>
</template>
