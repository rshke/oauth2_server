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
        ref?: HTMLHeadingElement | null;
    } = $props();
</script>

<h3
    bind:this={ref}
    class={cn("text-2xl font-semibold leading-none tracking-tight", className)}
    {...restProps}
>
    {@render children?.()}
</h3>
