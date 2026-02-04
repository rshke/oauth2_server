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
        ref?: HTMLParagraphElement | null;
    } = $props();
</script>

<p
    bind:this={ref}
    class={cn("text-sm text-muted-foreground", className)}
    {...restProps}
>
    {@render children?.()}
</p>
