<script lang="ts">
    import { Button } from "$lib/components/ui/button";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";
    import {
        Card,
        CardContent,
        CardDescription,
        CardFooter,
        CardHeader,
        CardTitle,
    } from "$lib/components/ui/card";
</script>

<div class="flex items-center justify-center min-h-screen bg-gray-100">
    <Card class="w-[350px]">
        <CardHeader>
            <CardTitle>Login</CardTitle>
            <CardDescription>
                Enter your credentials to access your account.
            </CardDescription>
        </CardHeader>
        <CardContent>
            <form>
                <div class="grid w-full items-center gap-4">
                    <div class="flex flex-col space-y-1.5">
                        <Label for="username">Username</Label>
                        <Input id="username" placeholder="Your username" />
                    </div>
                    <div class="flex flex-col space-y-1.5">
                        <Label for="password">Password</Label>
                        <Input
                            id="password"
                            type="password"
                            placeholder="Your password"
                        />
                    </div>
                </div>
            </form>
        </CardContent>
        <CardFooter class="flex justify-between">
            <Button variant="outline">Cancel</Button>
            <Button>Login</Button>
        </CardFooter>
    </Card>
</div>
