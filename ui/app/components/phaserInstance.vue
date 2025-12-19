<script setup>
import { MainScene } from '@/game/scenes/mainScene';

const props = defineProps({
    worldId: {
        type: Number,
        required: true,
    },
});

const containerId = 'phaser-game-container';
let gameInstance = null;

onMounted(async () => {
    const { default: Phaser } = await import('phaser');

    const config = {
        type: Phaser.AUTO,
        width: '100%',
        height: '100%',
        parent: containerId,
        backgroundColor: '#1c1917',
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

    gameInstance.scene.start('MainScene', { worldId: props.worldId });
});

onUnmounted(() => {
    if (gameInstance) {
        gameInstance.destroy(true);
        gameInstance = null;
    }
});
</script>

<template>
    <div :id="containerId" class="h-full w-full" />
</template>

<style scoped></style>
