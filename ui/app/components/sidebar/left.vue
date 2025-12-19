<script lang="ts" setup>
const toggleFreeCam = () => {
    window.dispatchEvent(new CustomEvent('vivarium-toggle-free-cam'));
};
</script>

<template>
    <div
        class="absolute top-4 left-4 h-[calc(100vh-2rem)] w-96 rounded-lg border-4 border-amber-800
            bg-amber-900 p-1 shadow-2xl shadow-black"
    >
        <!-- Inner Frame -->
        <div class="flex h-full flex-col rounded border-2 border-amber-700/50 bg-amber-900 p-4">
            <h2
                class="mb-6 border-b-2 border-amber-800 pb-2 text-center font-serif text-2xl
                    font-bold text-amber-100 drop-shadow-md"
            >
                Debug Tools
            </h2>

            <button
                class="focus:ring-0ss rounded border-2 border-stone-600 bg-stone-700 px-4 py-2
                    font-serif font-bold text-stone-200 shadow-lg transition-colors
                    hover:bg-stone-600 focus:outline-none active:translate-y-0.5
                    active:bg-stone-800"
                @click="toggleFreeCam"
            >
                Toggle Free Cam
            </button>
        </div>
    </div>
</template>

<style scoped></style>
