import time

from rich.console import Console
from rich.live    import Live
from rich.panel   import Panel
from rich.text    import Text
from rich.style   import Style
from rich         import box

class FancyLogger:
    def __init__(
        self,
        console: Console,
        max_visible: int = None
    ):
        self.console         = console
        self.max_visible     = max_visible
        self.entries         = []
        self.total_processed = 0
        self.stats           = {}
        self.total_size      = 0
        self.start_time      = None

        self.live   = Live(
            console            = console,
            auto_refresh       = True,
            vertical_overflow  = 'crop',
            refresh_per_second = 10
        )
        self.styles = [
            Style( color = 'white',        dim = False ),
            Style( color = 'white',        dim = True  ),
            Style( color = 'bright_black'              ),
        ]

    def start(
        self
    ):
        self.start_time = time.time()
        self.console.clear()
        self.live.start()
        self.live.update( self._build_panel() )

    def stop(
        self
    ):
        self.live.update( self._build_panel() )
        self.live.stop()

    def add_entry(
        self, info: dict
    ):
        self.total_processed += 1
        
        cat_dict  = info.get( 'category', { 'name': 'OTHER', 'color': 'white' } )
        cat_name  = cat_dict.get( 'name', 'OTHER' )
        file_size = info.get( 'size_bytes', 0 )
        
        if cat_name not in self.stats:
            self.stats[ cat_name ] = { 'count': 0, 'size_bytes': 0, 'color': cat_dict.get( 'color', 'white' ) }
        
        self.stats[ cat_name ][ 'count' ]      += 1
        self.stats[ cat_name ][ 'size_bytes' ] += file_size
        self.total_size                        += file_size
        
        self.entries.append( info )

        if self.max_visible and len( self.entries ) > self.max_visible:
            self.entries.pop( 0 )
        
        self.live.update( self._build_panel() )

    def _build_panel(
        self
    ) -> Panel:
        term_width     = self.console.size.width
        term_height    = self.console.size.height
        max_line_width = term_width - 4
        
        log_height       = max( 3, term_height - 7 )
        available_height = log_height - 2
        
        if self.max_visible:
            visible_count = self.max_visible
        else:
            visible_count = max( 1, available_height // 8 )

        visible_count   = min( visible_count, len( self.entries ) )
        visible_entries = self.entries[ -visible_count: ] if visible_count > 0 else []
        
        if not visible_entries:
            log_text = Text( '\n' * available_height )
            log_text.append( 'Waiting for files...', style = 'dim italic' )
        else:
            blocks = []

            for i, entry in enumerate( reversed( visible_entries ) ):
                # Определяем стиль яркости
                base_style = Style( color = 'white' )
                
                cat_dict  = entry.get( 'category', { 'name': 'OTHER', 'color': 'white' } )
                cat_name  = cat_dict.get( 'name', 'остальное' )
                cat_color = cat_dict.get( 'color', 'white' )
                
                ext = entry[ 'type' ].lstrip( '.' )
                
                block = Text()
                
                # Строка с именем и категорией (цветная!)
                block.append( 'Processing ', style = base_style )
                block.append( _truncate( entry[ 'name' ], max_line_width - 30 ), style = Style( color = cat_color ) )
                block.append( '\n' )
                
                # Остальные строки без разметки
                block.append( f'├─Category: ', style = base_style )
                block.append( f'{cat_name}' + '\n', style = Style( color = cat_color ) )
                block.append( f'├─Type:     {ext}' + '\n', style = base_style )
                block.append( f'├─Size:     {_format_size( entry.get( 'size_bytes', 0 ) )}' + '\n', style = base_style )
                block.append( _truncate( f'├─Source:   {entry[ 'source' ]}', max_line_width ) + '\n', style = base_style )
                block.append( _truncate( f'├─Dest:     {entry[ 'dest' ]}', max_line_width ) + '\n', style = base_style )
                block.append( '└─NSFW Score | Furry Score\n', style = base_style)
                block.append( f'  {entry[ 'nsfw_score' ]:.4f}       {entry[ 'furry_score' ]:.4f}\n', style = base_style )
                block.append( ' ' * ( max_line_width - 2 ) + '\n' )
                blocks.append( block )
            
            log_text = Text()

            for b in reversed( blocks ):
                log_text.append( b )
            
            current_lines = visible_count * 8
            missing_lines = max( 0, available_height - current_lines )

            if missing_lines > 0:
                log_text.append( '\n' * missing_lines )
        
        # Строка статистики (цветная!)
        elapsed     = time.time() - self.start_time if self.start_time else 0
        sorted_cats = sorted( self.stats.items(), key = lambda x: x[ 1 ][ 'count' ], reverse=True )
        
        stats_text = Text()
        first      = True

        for cat_name, cat_data in sorted_cats:
            if not first:
                stats_text.append(' - ')
                
            first = False
            
            count          = cat_data[ 'count' ]
            size_formatted = _format_size( cat_data[ 'size_bytes' ] )
            color          = cat_data.get( 'color', 'white' )
            
            stats_text.append( f'{cat_name}: ', style = Style( color = color ) )
            stats_text.append( f'{count} [{size_formatted}]', style = 'white' )
    
        stats_text.append( ' ' )
        stats_text.append( f'│ Total: {self.total_processed} ', style = 'white' )
        stats_text.append( f'│ Transfered: {_format_size( self.total_size )} ', style = 'white' )

        if elapsed < 60:
            time_str = f'{elapsed:.1f}с'
        else:
            mins     = int( elapsed // 60 )
            secs     = int( elapsed % 60 )
            time_str = f'{mins}m{secs}s'
        stats_text.append( f'| Time elapsed: {time_str}', style='white' )
        
        # Собираем всё
        final_text = Text()
        final_text.append( stats_text )
        final_text.append( '\n' + ( '─' * ( max_line_width - 2 ) ) + '\n', style = 'dim' )
        final_text.append( log_text )
        
        return Panel(
            final_text,
            box          = box.DOUBLE,
            border_style = 'cornflower_blue',
            padding      = ( 0, 1 ),
            title        = '[bold light_sky_blue1]FUR[/bold light_sky_blue1][bold light_sky_blue1]TRATOR[/bold light_sky_blue1]',
            height       = term_height
        )
    
def _truncate(
    text: str,
    max_width: int
) -> str:
    if len(text) <= max_width:
        return text
    return text[ :max_width - 3 ] + '...'

def _format_size(
    size_bytes: int
) -> str:
    if size_bytes < 1024:
        return f'{size_bytes}B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f}KB'
    else:
        return f'{size_bytes / ( 1024 * 1024 ):.1f}MB'