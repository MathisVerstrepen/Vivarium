<script setup>
import { MainScene } from '@/game/scenes/mainScene';

const containerId = 'phaser-game-container';
let gameInstance = null;

onMounted(async () => {
    // CRITICAL: Dynamically import Phaser here.
    const { default: Phaser } = await import('phaser');

    const config = {
        type: Phaser.AUTO,
        width: '100%',
        height: '100%',
        parent: containerId,
        backgroundColor: '#ffffff',
        physics: {
            default: 'arcade',
            arcade: {
                gravity: { y: 0 },
                debug: true,
            },
        },
        scene: [MainScene],
        scale: {
            mode: Phaser.Scale.RESIZE,
            autoCenter: Phaser.Scale.CENTER_BOTH,
        },
    };

    gameInstance = new Phaser.Game(config);
});

onUnmounted(() => {
    if (gameInstance) {
        gameInstance.destroy(true);
        gameInstance = null;
    }
});
</script>

<template>
    <div :id="containerId" class="flex items-center justify-center bg-white" />
</template>

<style scoped></style>
