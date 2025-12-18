<template>
    <div class="flex h-screen w-screen items-center justify-center bg-black">
        <ClientOnly>
            <PhaserInstance />
            <template #fallback>
                <div class="text-white">Loading...</div>
            </template>
        </ClientOnly>
    </div>
</template>

<style></style>
