<script setup>
import { MainScene } from '@/game/scenes/mainScene';

const containerId = 'phaser-game-container';
let gameInstance = null;

onMounted(async () => {
    // CRITICAL: Dynamically import Phaser here.
    // This ensures it ONLY loads on the client-side (browser).
    const { default: Phaser } = await import('phaser');

    const config = {
        type: Phaser.AUTO,
        width: 800,
        height: 600,
        parent: containerId, // Matches the div ID above
        physics: {
            default: 'arcade',
            arcade: {
                gravity: { y: 0 }, // Top-down games usually have 0 gravity
                debug: true,
            },
        },
        scene: [MainScene],
    };

    gameInstance = new Phaser.Game(config);
});

onUnmounted(() => {
    // Cleanup to prevent memory leaks when navigating away
    if (gameInstance) {
        gameInstance.destroy(true);
        gameInstance = null;
    }
});
</script>

<template>
    <div :id="containerId" class="flex h-screen w-screen items-center justify-center bg-black" />
</template>

<style scoped></style>
