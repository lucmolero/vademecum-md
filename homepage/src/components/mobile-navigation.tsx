import {
  Root as DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@animate-ui/react/primitives/radix-ui/dropdown-menu';

const links = [
  ['Skill', '#skill'],
  ['Recursos', '#recursos'],
  ['Assistente', '#assistente'],
  ['Biblioteca', './biblioteca/'],
] as const;

export function MobileNavigation() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button type="button" aria-label="Abrir navegação" className="flex size-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-foreground sm:hidden">
          <svg aria-hidden="true" viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" sideOffset={8} className="z-[80] min-w-48 rounded-xl border border-border bg-background p-1.5 text-foreground shadow-lg">
        {links.map(([label, href]) => (
          <DropdownMenuItem key={href} asChild>
            <a href={href} className="flex min-h-10 items-center rounded-lg px-3 text-sm text-foreground outline-none focus:bg-accent">{label}</a>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
