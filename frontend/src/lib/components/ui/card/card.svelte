<script lang="ts">
    import { cn } from "$lib/utils.js";

    let {
        ref = $bindable(null),
        class: className,
        children,
        ...restProps
    }: {
        class?: string;
        children?: any;
        ref?: HTMLDivElement | null;
    } = $props();
</script>

<div
    bind:this={ref}
    class={cn(
        "rounded-lg border bg-card text-card-foreground shadow-sm",
        className,
    )}
    {...restProps}
>
    {@render children?.()}
</div>
