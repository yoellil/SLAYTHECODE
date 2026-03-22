"""
CODE SPIRE — Roguelike Deck Builder
7 classes, 15-floor procedural map, HEROSCRIPT card-programming language.
"""

# Standard library and GUI imports used throughout the game.
import random
import tkinter as tk
from tkinter import scrolledtext, messagebox
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
import re
import math
import os


try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available. Using placeholder graphics.")



VERSION = "2.0.0"
GAME_NAME = "CODE SPIRE"
SUBTITLE = "A Roguelike Deck Builder"



# Loads PNG sprites from the Assets folder and caches them as PhotoImage objects.
class SpriteManager:
    """Manages all game sprites and images. Loads from Assets folder."""

    def __init__(self, asset_folder: str = "Assets"):
        self.asset_folder = asset_folder
        self.sprites: Dict[str, ImageTk.PhotoImage] = {}
        self.raw_images: Dict[str, Image.Image] = {}
        self._generated = False
        self._initialized = False

    def initialize(self):
        """Initialize sprites. Must be called after Tk root is created."""
        if self._initialized:
            return

        self._initialized = True
        self._load_all_sprites()

    def _load_all_sprites(self):
        """Load all sprites from the Assets folder."""
        if not PIL_AVAILABLE:
            print("PIL not available, using colored shapes instead")
            return

        if not os.path.exists(self.asset_folder):
            print(f"Assets folder not found: {self.asset_folder}")
            return

        try:

            class_sprites = {
                "Ironclad": "Ironclad-removebg-preview.png",
                "Silent": "Silent-removebg-preview.png",
                "Defect": "Defect-removebg-preview.png",
                "Watcher": "Watcher-removebg-preview.png",
                "Glass Cannon": "Glass_Cannon-removebg-preview.png",
                "Necromancer": "Necromancer-removebg-preview.png",
                "Chronomancer": "Chronomancer-removebg-preview.png",
            }

            for key, filename in class_sprites.items():
                self._load_sprite(key, filename, (64, 64))


            enemy_sprites = {
                "Minor Glitch": "Minor_Glitch-removebg-preview.png",
                "Stray Bug": "Stray_Bug-removebg-preview.png",
                "Loose Pointer": "Loose_Pointer-removebg-preview.png",
                "Bug Swarm": "Bug_Swarm-removebg-preview.png",
                "The Compiler": "The_Compiler-removebg-preview.png",
                "Memory Leak": "Memory_Leak-removebg-preview.png",
                "Stack Overflow": "Stack_Overflow-removebg-preview.png",
                "Null Pointer": "Null_Pointer-removebg-preview.png",
                "Stack Phantom": "Stack_Phantom-removebg-preview.png",
                "Heap Horror": "Heap_Horror-removebg-preview.png",
                "Memory Beast": "Memory_Beast-removebg-preview.png",
                "The Garbage Collector": "The_Garbage_Collector-removebg-preview.png",
                "The Heart of the Spire": "The_Heart_of_the_Spire-removebg-preview.png",
            }

            for key, filename in enemy_sprites.items():
                self._load_sprite(key, filename, (64, 64))


            self.sprites["enemy_minion"] = self.sprites.get("Minor Glitch")
            self.sprites["enemy_normal"] = self.sprites.get("The Compiler")
            self.sprites["enemy_elite"] = self.sprites.get("Stack Phantom")
            self.sprites["enemy_boss"] = self.sprites.get("The Heart of the Spire")

            self._generated = True
            print(f"Loaded {len(self.sprites)} sprites from Assets folder!")
        except Exception as e:
            print(f"Error loading sprites: {e}")

    def _load_sprite(self, key: str, filename: str, target_size: Tuple[int, int] = (64, 64)):
        """Load a single sprite from file."""
        path = os.path.join(self.asset_folder, filename)
        if not os.path.exists(path):
            print(f"Missing: {filename}")
            return False

        try:
            img = Image.open(path)


            if img.mode != 'RGBA':
                img = img.convert('RGBA')



            data = img.getdata()
            new_data = []
            for item in data:

                if len(item) == 4:
                    r, g, b, a = item
                else:
                    r, g, b = item
                    a = 255



                brightness = (r + g + b) / 3


                if brightness < 30 or brightness > 220:

                    new_data.append((r, g, b, 0))
                else:

                    new_data.append((r, g, b, a))


            img = Image.new('RGBA', img.size)
            img.putdata(new_data)


            img = img.resize(target_size, Image.Resampling.LANCZOS)
            self.raw_images[key] = img
            self.sprites[key] = ImageTk.PhotoImage(img)
            print(f"Loaded sprite: {filename}")
            return True
        except Exception as e:
            print(f"Failed to load {filename}: {e}")
            return False

    def get_sprite(self, key: str) -> Optional[ImageTk.PhotoImage]:
        """Get a sprite by key."""
        if not self._generated and not self._initialized:
            self.initialize()
        return self.sprites.get(key)

    def get_class_sprite(self, class_name: str) -> Optional[ImageTk.PhotoImage]:
        """Get the appropriate sprite for a character class."""
        if not self._generated and not self._initialized:
            self.initialize()


        return self.sprites.get(class_name)

    def get_enemy_sprite(self, enemy_name: str = "normal") -> Optional[ImageTk.PhotoImage]:
        """Get sprite for enemy by name."""
        if not self._generated and not self._initialized:
            self.initialize()


        sprite = self.sprites.get(enemy_name)
        if sprite:
            return sprite


        type_mappings = {
            "minion": self.sprites.get("enemy_minion"),
            "normal": self.sprites.get("enemy_normal"),
            "elite": self.sprites.get("enemy_elite"),
            "boss": self.sprites.get("enemy_boss"),
        }

        return type_mappings.get(enemy_name.lower()) or self.sprites.get("enemy_normal")


sprite_manager = SpriteManager()



# Enum of every token category the HEROSCRIPT lexer can produce.
class TokenType(Enum):
    """Token types for the HEROSCRIPT language lexer."""
    DATATYPE = "DATATYPE"
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    ASSIGN_OP = "ASSIGN_OP"
    FIXED_ASSIGN = "FIXED_ASSIGN"
    DELIMITER = "DELIMITER"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    NEWLINE = "NEWLINE"
    OPERATOR = "OPERATOR"
    NUMERIC = "NUMERIC"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    COMMENT = "COMMENT"
    WHITESPACE = "WHITESPACE"
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"

# Two combat stances for the Watcher class: defensive vs aggressive.
class Stance(Enum):
    """Stance system for CIRCUITVOICE: two processing modes."""
    OBSERVATION = "OBSERVATION"
    INTERVENTION = "INTERVENTION"

# One lexical unit produced by the Lexer (type, raw value, source position).
@dataclass
class Token:
    """Represents a single token in the HEROSCRIPT language."""
    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.value}, '{self.value}', {self.line}:{self.column})"

# Raised when the Lexer encounters a character it cannot classify.
class LexerError(Exception):
    """Exception raised when a lexical error occurs."""
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer Error at {line}:{column}: {message}")

# Converts raw HEROSCRIPT source text into a flat list of Token objects.
class Lexer:
    """
    Tokenizer for the HEROSCRIPT programming language.
    Converts source code into a stream of tokens.
    """

    DATATYPES = {'bolt', 'scroll', 'flag', 'digit', 'char'}

    KEYWORDS = {
        'speak', 'repeat', 'until', 'break', 'end', 'close', 'test', 'fail', 'pass',
        'true', 'false',
        'and', 'or', 'not',
        'enemy',
    }

    OPERATORS = {'+', '-', '*', '/', '%', '==', '!=', '>', '<', '>=', '<=', '=~', '!~'}

    def __init__(self, code: str):
        self.code = code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def current_char(self) -> Optional[str]:
        """Get the current character without advancing."""
        if self.position >= len(self.code):
            return None
        return self.code[self.position]

    def peek(self, offset: int = 1) -> Optional[str]:
        """Peek at a character ahead without advancing."""
        pos = self.position + offset
        if pos >= len(self.code):
            return None
        return self.code[pos]

    def advance(self):
        """Advance to the next character."""
        if self.position < len(self.code):
            if self.code[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

    def skip_whitespace(self):
        """Skip whitespace characters."""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()

    def skip_comment(self):
        """Skip comment lines starting with #."""
        while self.current_char() and self.current_char() != '\n':
            self.advance()

    def read_string(self, quote_char: str) -> str:
        """Read a string literal."""
        self.advance()
        value = ""
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                if self.current_char() == 'n':
                    value += '\n'
                elif self.current_char() == 't':
                    value += '\t'
                elif self.current_char() == '\\':
                    value += '\\'
                else:
                    value += self.current_char()
            else:
                value += self.current_char()
            self.advance()
        if self.current_char() == quote_char:
            self.advance()
        return value

    def read_number(self) -> str:
        """Read a numeric literal."""
        value = ""
        has_decimal = False
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_decimal:
                    break
                has_decimal = True
            value += self.current_char()
            self.advance()
        return value

    def read_identifier(self) -> str:
        """Read an identifier or keyword."""
        value = ""
        while self.current_char() and (self.current_char().isalnum() or self.current_char() in '_-'):
            value += self.current_char()
            self.advance()
        return value

    def tokenize(self) -> List[Token]:
        """Convert source code into a list of tokens."""
        self.tokens = []

        while self.position < len(self.code):
            char = self.current_char()
            line, col = self.line, self.column


            if char in ' \t\r':
                self.skip_whitespace()
                continue


            if char == '#':
                self.skip_comment()
                continue


            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', line, col))
                self.advance()
                continue


            if char in '"\'':
                string_value = self.read_string(char)
                self.tokens.append(Token(TokenType.STRING, string_value, line, col))
                continue


            if char.isdigit() or (char == '.' and self.peek() and self.peek().isdigit()):
                num_value = self.read_number()
                self.tokens.append(Token(TokenType.NUMERIC, num_value, line, col))
                continue


            if char.isalpha() or char == '_':
                ident_value = self.read_identifier()
                lower = ident_value.lower()
                if lower in self.DATATYPES:
                    self.tokens.append(Token(TokenType.DATATYPE, lower, line, col))
                elif lower in ('true', 'false'):
                    self.tokens.append(Token(TokenType.BOOLEAN, lower, line, col))
                elif lower in self.KEYWORDS:
                    self.tokens.append(Token(TokenType.KEYWORD, lower, line, col))
                else:

                    self.tokens.append(Token(TokenType.IDENTIFIER, ident_value, line, col))
                continue


            two_char = char + (self.peek() or '')
            if two_char in self.OPERATORS:
                self.tokens.append(Token(TokenType.OPERATOR, two_char, line, col))
                self.advance()
                self.advance()
                continue


            if char in '+-*/%=<>!':
                self.tokens.append(Token(TokenType.OPERATOR, char, line, col))
                self.advance()
                continue


            if char == '~':
                if self.peek() == '~':
                    self.tokens.append(Token(TokenType.FIXED_ASSIGN, '~~', line, col))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.ASSIGN_OP, '~', line, col))
                    self.advance()
                continue


            if char == '.':
                self.tokens.append(Token(TokenType.DELIMITER, '.', line, col))
                self.advance()
                continue


            if char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', line, col))
                self.advance()
                continue
            if char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', line, col))
                self.advance()
                continue


            if char == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{', line, col))
                self.advance()
                continue
            if char == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}', line, col))
                self.advance()
                continue


            if char == '[':
                self.tokens.append(Token(TokenType.LBRACKET, '[', line, col))
                self.advance()
                continue
            if char == ']':
                self.tokens.append(Token(TokenType.RBRACKET, ']', line, col))
                self.advance()
                continue


            if char == ':':
                self.tokens.append(Token(TokenType.DELIMITER, ':', line, col))
                self.advance()
                continue


            self.tokens.append(Token(TokenType.UNKNOWN, char, line, col))
            self.advance()


        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens

# Raised when the Parser finds a structural error in the token stream.
class ParserError(Exception):
    """Exception raised when a parsing error occurs."""
    pass

# Turns a Token list into an AST (list of statement dicts) for execution.
class Parser:
    """
    Parser for the HEROSCRIPT language.
    Converts a stream of tokens into an abstract syntax tree (AST).
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0

    def current_token(self) -> Token:
        """Get the current token."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return self.tokens[-1]

    def peek(self, offset: int = 1) -> Token:
        """Peek at a future token."""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]

    def advance(self) -> Token:
        """Advance to the next token and return the previous one."""
        token = self.current_token()
        self.position += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        """Expect a specific token type and advance."""
        token = self.current_token()
        if token.type != token_type:
            raise ParserError(f"Expected {token_type.value}, got {token.type.value}")
        return self.advance()

    def parse(self) -> List[Dict[str, Any]]:
        """Parse tokens into a list of statements."""
        statements = []
        while self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements

    def parse_statement(self) -> Optional[Dict[str, Any]]:
        """Parse a single statement."""
        token = self.current_token()


        if token.type == TokenType.DELIMITER:
            self.advance()
            return None


        if token.type == TokenType.NEWLINE:
            self.advance()
            return None


        if token.type == TokenType.EOF:
            return None


        if token.type == TokenType.DATATYPE:
            return self.parse_declaration()


        if token.type == TokenType.KEYWORD and token.value == 'speak':
            return self.parse_speak()


        if token.type == TokenType.KEYWORD and token.value == 'repeat':
            return self.parse_repeat()


        if token.type == TokenType.KEYWORD and token.value == 'break':
            return self.parse_break()


        if token.type == TokenType.KEYWORD and token.value == 'test':
            return self.parse_test()


        self.advance()
        return {'type': 'unknown', 'value': token.value}

    def parse_declaration(self) -> Dict[str, Any]:
        """Parse a variable declaration: bolt x ~ 6."""
        datatype = self.advance()
        var_name = self.expect(TokenType.IDENTIFIER)


        assign_op = None
        if self.current_token().type in (TokenType.ASSIGN_OP, TokenType.FIXED_ASSIGN):
            assign_op = self.advance()


        value = self.parse_expression()


        if self.current_token().type == TokenType.DELIMITER:
            self.advance()

        return {
            'type': 'declaration',
            'datatype': datatype.value,
            'name': var_name.value,
            'assign_op': assign_op.value if assign_op else None,
            'value': value,
            'is_roll': assign_op.type == TokenType.ASSIGN_OP if assign_op else False
        }

    def parse_expression(self) -> Dict[str, Any]:
        """Parse an expression."""
        return self.parse_additive()

    def parse_additive(self) -> Dict[str, Any]:
        """Parse addition and subtraction."""
        left = self.parse_multiplicative()

        while self.current_token().type == TokenType.OPERATOR and self.current_token().value in '+-':
            op = self.advance()
            right = self.parse_multiplicative()
            left = {'type': 'binary_op', 'op': op.value, 'left': left, 'right': right}

        return left

    def parse_multiplicative(self) -> Dict[str, Any]:
        """Parse multiplication, division, and modulo."""
        left = self.parse_primary()

        while self.current_token().type == TokenType.OPERATOR and self.current_token().value in '*/%':
            op = self.advance()
            right = self.parse_primary()
            left = {'type': 'binary_op', 'op': op.value, 'left': left, 'right': right}

        return left

    def parse_primary(self) -> Dict[str, Any]:
        """Parse primary expressions."""
        token = self.current_token()


        if token.type == TokenType.NUMERIC:
            self.advance()
            return {'type': 'number', 'value': float(token.value)}


        if token.type == TokenType.BOOLEAN:
            self.advance()
            return {'type': 'boolean', 'value': token.value == 'true'}


        if token.type == TokenType.STRING:
            self.advance()
            return {'type': 'literal', 'value': token.value}


        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return {'type': 'identifier', 'name': token.value}


        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr


        if token.type == TokenType.KEYWORD:
            self.advance()
            return {'type': 'identifier', 'name': token.value}


        return {'type': 'literal', 'value': token.value}

    def parse_speak(self) -> Dict[str, Any]:
        """Parse a speak statement: speak "Hello"."""
        self.advance()
        message = self.expect(TokenType.STRING)
        if self.current_token().type == TokenType.DELIMITER:
            self.advance()
        return {'type': 'speak', 'message': message.value}

    def parse_break(self) -> Dict[str, Any]:
        """Parse a break statement for loops."""
        self.advance()
        if self.current_token().type == TokenType.DELIMITER:
            self.advance()
        return {'type': 'break'}

    def parse_repeat(self) -> Dict[str, Any]:
        """Parse a repeat loop with indent-style block after ':'."""
        self.advance()
        count_expr = None
        condition = None
        body = []


        if self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'until':
            self.advance()
            condition = self.parse_expression()


        elif self.current_token().type in (TokenType.NUMERIC, TokenType.IDENTIFIER):
            count_expr = self.parse_expression()


        if self.current_token().type != TokenType.DELIMITER or self.current_token().value != ':':
            raise ParserError("Expected ':' after repeat header")
        self.advance()


        if self.current_token().type != TokenType.NEWLINE:
            raise ParserError("Expected newline after ':' in repeat block")


        while self.current_token().type == TokenType.NEWLINE:
            self.advance()


        while self.current_token().type != TokenType.EOF:
            if self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'end':
                self.advance()
                if self.current_token().type == TokenType.DELIMITER:
                    self.advance()
                break

            if self.current_token().type == TokenType.NEWLINE:
                self.advance()
                continue

            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)

        return {'type': 'repeat', 'count': count_expr, 'condition': condition, 'body': body}

    def parse_test(self) -> Dict[str, Any]:
        """
        Parse a test (if/else) statement.

        Supported syntax:
            test <condition>:
                <pass_body statements>
            fail:
                <fail_body statements>
            close.

        'pass' body = executes when condition is TRUE (analogous to 'if true').
        'fail' body = executes when condition is FALSE (analogous to 'else').
        """
        self.advance()


        condition = self.parse_expression()


        if self.current_token().type == TokenType.DELIMITER and self.current_token().value == ':':
            self.advance()


        while self.current_token().type == TokenType.NEWLINE:
            self.advance()


        pass_body = []
        while self.current_token().type != TokenType.EOF:
            t = self.current_token()
            if t.type == TokenType.KEYWORD and t.value in ('fail', 'close'):
                break
            if t.type == TokenType.NEWLINE:
                self.advance()
                continue
            stmt = self.parse_statement()
            if stmt:
                pass_body.append(stmt)


        fail_body = []
        if self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'fail':
            self.advance()

            if self.current_token().type == TokenType.DELIMITER and self.current_token().value == ':':
                self.advance()

            while self.current_token().type == TokenType.NEWLINE:
                self.advance()

            while self.current_token().type != TokenType.EOF:
                t = self.current_token()
                if t.type == TokenType.KEYWORD and t.value == 'close':
                    break
                if t.type == TokenType.NEWLINE:
                    self.advance()
                    continue
                stmt = self.parse_statement()
                if stmt:
                    fail_body.append(stmt)


        if self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'close':
            self.advance()
        if self.current_token().type == TokenType.DELIMITER:
            self.advance()

        return {
            'type': 'test',
            'condition': condition,
            'pass': pass_body,
            'fail': fail_body,
        }

# Walks the AST, builds a symbol table, and catches type / name errors.
class SemanticAnalyzer:
    """
    Semantic analyzer for HEROSCRIPT.
    Validates and transforms the AST.
    """

    def __init__(self, ast: List[Dict[str, Any]]):
        self.ast = ast
        self.symbol_table: Dict[str, Any] = {}
        self.errors: List[str] = []

    def analyze(self) -> Dict[str, Any]:
        """Analyze the AST and return analysis results."""
        for stmt in self.ast:
            self.analyze_statement(stmt)
        return {
            'symbol_table': self.symbol_table,
            'errors': self.errors,
            'declarations': [s for s in self.ast if s.get('type') == 'declaration']
        }

    def analyze_statement(self, stmt: Dict[str, Any]):
        """Analyze a single statement."""
        if stmt['type'] == 'declaration':
            self.analyze_declaration(stmt)
        elif stmt['type'] == 'speak':
            pass
        elif stmt['type'] == 'break':
            pass
        elif stmt['type'] == 'repeat':
            for inner in stmt.get('body', []):
                self.analyze_statement(inner)

    def analyze_declaration(self, stmt: Dict[str, Any]):
        """Analyze a variable declaration."""
        name = stmt['name']
        if name in self.symbol_table:
            self.errors.append(f"Variable '{name}' already declared")
        else:
            self.symbol_table[name] = {
                'datatype': stmt['datatype'],
                'is_roll': stmt.get('is_roll', False),
                'value': stmt.get('value')
            }

# Sentinel exception used to exit repeat loops when "break." is executed.
class BreakException(Exception):
    """Raised by break statements inside loops."""
    pass

# Runs the full Lex→Parse→Analyse→Execute pipeline on a HEROSCRIPT snippet.
class HeroScriptCompiler:
    """
    Main compiler for the HEROSCRIPT language.
    Compiles code snippets into executable game actions.
    """

    def __init__(self, code: str):
        self.code = code
        self.lexer = Lexer(code)
        self.tokens: List[Token] = []
        self.ast: List[Dict[str, Any]] = []
        self.symbol_table: Dict[str, Any] = {}
        self.output: List[str] = []
        self.rolls: List[int] = []

    def compile(self) -> Dict[str, Any]:
        """Compile the code and return results."""
        try:

            self.tokens = self.lexer.tokenize()


            parser = Parser(self.tokens)
            self.ast = parser.parse()


            analyzer = SemanticAnalyzer(self.ast)
            result = analyzer.analyze()
            self.symbol_table = result['symbol_table']


            self.execute()

            return {
                'success': True,
                'symbol_table': self.symbol_table,
                'output': self.output,
                'rolls': self.rolls,
                'errors': result['errors']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'symbol_table': self.symbol_table,
                'output': self.output,
                'rolls': self.rolls
            }

    def execute(self):
        """Execute the AST."""
        for stmt in self.ast:
            self.execute_statement(stmt)

    def execute_statement(self, stmt: Dict[str, Any]):
        """Execute a single statement."""
        if stmt['type'] == 'declaration':
            self.execute_declaration(stmt)
        elif stmt['type'] == 'speak':
            self.output.append(stmt['message'])
        elif stmt['type'] == 'break':
            raise BreakException()
        elif stmt['type'] == 'repeat':
            count = stmt.get('count')
            condition = stmt.get('condition')
            body = stmt.get('body', [])

            def run_body_once():
                for body_stmt in body:
                    try:
                        self.execute_statement(body_stmt)
                    except BreakException:
                        raise


            if count is not None:
                repeat_times = int(self.evaluate(count)) if isinstance(count, dict) else int(count)
                for i in range(max(0, repeat_times)):
                    try:
                        run_body_once()
                    except BreakException:
                        break
                    if condition is not None and self.evaluate(condition):
                        break
                return


            if condition is not None:
                safety = 0
                while safety < 1000:
                    try:
                        run_body_once()
                    except BreakException:
                        break
                    if self.evaluate(condition):
                        break
                    safety += 1
                return


            try:
                run_body_once()
            except BreakException:
                pass

    def execute_declaration(self, stmt: Dict[str, Any]):
        """Execute a variable declaration."""
        name = stmt['name']
        value = self.evaluate(stmt['value'])

        if stmt.get('is_roll', False):

            sides = int(value)
            roll_result = random.randint(1, sides)
            self.rolls.append(roll_result)
            self.symbol_table[name] = roll_result
        else:
            self.symbol_table[name] = value

    def evaluate(self, expr: Dict[str, Any]) -> Any:
        """Evaluate an expression."""
        if expr['type'] == 'number':
            return expr['value']
        elif expr['type'] == 'identifier':
            return self.symbol_table.get(expr['name'], 0)
        elif expr['type'] == 'binary_op':
            left = self.evaluate(expr['left'])
            right = self.evaluate(expr['right'])
            op = expr['op']
            if op == '+':
                result = left + right
            elif op == '-':
                result = left - right
            elif op == '*':
                result = left * right
            elif op == '/':
                result = left / right if right != 0 else 0
            elif op == '%':
                result = left % right
            else:
                result = 0

            if 'roll' in str(left) or 'roll' in str(right):
                pass
            return result
        elif expr['type'] == 'boolean':
            return expr['value']
        else:
            return 0

# Roll one fair die with the given number of sides (1 … sides).
def roll_dice(sides: int) -> int:
    """Roll a die with the given number of sides."""
    return random.randint(1, sides)

# Parse a dice-pool string (e.g. "4d3", "6+4") and return individual roll results.
def roll_dice_pool(pool_str: str) -> List[int]:
    """
    Roll a pool of dice from a string like '4d3' or '6+4' (roll 6d4).
    Returns a list of individual roll results.
    FIX: '6+4' now means 6 four-sided dice (6d4), not 1d6+1d4.
    So '6+4' = roll 6 dice with 4 sides each, max damage = 24.
    """
    results = []
    parts = pool_str.replace(' ', '').split('+')



    if len(parts) == 2:
        try:
            num1 = int(parts[0])
            num2 = int(parts[1])

            for _ in range(num1):
                results.append(roll_dice(num2))
            return results
        except ValueError:
            pass


    for part in parts:
        if 'd' in part.lower():

            match = re.match(r'(\d*)d(\d+)', part.lower())
            if match:
                count = int(match.group(1)) if match.group(1) else 1
                sides = int(match.group(2))
                for _ in range(count):
                    results.append(roll_dice(sides))
        else:

            try:
                value = int(part)
                results.append(roll_dice(value))
            except ValueError:
                pass
    return results

# Full HEROSCRIPT card executor: tokenises, parses, then walks the AST.
# Returns a dict with damage/block/heal/strength rolls and any debuffs.
def execute_card_code(code: str, enemy: 'Enemy' = None) -> Dict[str, Any]:
    """
    Execute HEROSCRIPT card code via the full compiler pipeline and return game results.

    Supported constructs (per cheat sheet):
      bolt dmg  ~ N.          — roll 1dN damage
      bolt dmg  ~ N * M.      — roll N dice of M sides  (NdM)
      bolt dmg  ~ N + N.      — roll 2 dice of N sides each (2dN)
      bolt def  ~ N.          — roll 1dN block
      bolt heal ~ N.          — roll 1dN healing
      bolt pow  ~ N.          — gain N strength
      scroll debuff ~ "name" + N.  — apply debuff 'name' for 1dN turns
      repeat K:               — repeat body K times (body must be indented)
          bolt dmg ~ N.
      end.
      test enemy ~~ debuff:   — if enemy has debuff, run pass body; else fail body
          bolt dmg ~ N * M.
      fail:
          bolt dmg ~ N.
      close.
    """

    try:
        lexer  = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast    = parser.parse()
    except Exception as e:
        return {
            'success': False, 'error': str(e),
            'damage': 0, 'block': 0, 'heal': 0, 'strength': 0,
            'rolls': [], 'defense_rolls': [], 'heal_rolls': [], 'strength_rolls': [],
            'debuffs': [], 'symbol_table': {}
        }


    damage_rolls   = []
    defense_rolls  = []
    heal_rolls     = []
    strength_rolls = []
    debuffs_out    = []
    symbol_table   = {}


    def roll_expr(value_node: dict) -> List[int]:
        """
        Evaluate a dice expression node and return list of individual rolls.

        Rules (matching cheat sheet):
          number N           → roll 1dN  (single die with N sides)
          binary_op N * M    → roll NdM  (N dice of M sides)
          binary_op N + M    → roll 1dN + 1dM  (two separate dice)
          Three+ addends     → one die per addend
        """
        if value_node is None:
            return []

        vtype = value_node.get('type')

        if vtype == 'number':
            sides = max(1, int(value_node['value']))
            return [random.randint(1, sides)]

        if vtype == 'identifier':

            val = symbol_table.get(value_node['name'], 1)
            return [random.randint(1, max(1, int(val)))]

        if vtype == 'binary_op':
            op    = value_node['op']
            left  = value_node['left']
            right = value_node['right']

            if op == '*':

                count = max(1, int(eval_numeric(left)))
                sides = max(1, int(eval_numeric(right)))
                return [random.randint(1, sides) for _ in range(count)]

            if op == '+':

                return _flatten_add_rolls(value_node)

        return [1]

    def _flatten_add_rolls(node: dict) -> List[int]:
        """Recursively flatten a chain of + nodes into one roll per term."""
        if node.get('type') != 'binary_op' or node.get('op') != '+':
            return roll_expr(node)
        return _flatten_add_rolls(node['left']) + _flatten_add_rolls(node['right'])

    def eval_numeric(node: dict) -> float:
        """Evaluate a node to a plain number (no dice rolling — just arithmetic)."""
        if node is None:
            return 0
        t = node.get('type')
        if t == 'number':
            return node['value']
        if t == 'identifier':
            return symbol_table.get(node['name'], 0)
        if t == 'binary_op':
            l = eval_numeric(node['left'])
            r = eval_numeric(node['right'])
            op = node['op']
            if op == '+': return l + r
            if op == '-': return l - r
            if op == '*': return l * r
            if op == '/': return l / r if r else 0
            if op == '%': return l % r if r else 0
        return 0

    def eval_condition(node: dict) -> bool:
        """
        Evaluate a test condition.
        Special case: 'enemy ~~ <debuff_name>' checks if enemy has that debuff.
        General case: evaluate as numeric comparison.
        """
        if node is None:
            return False
        t = node.get('type')










        if t == 'identifier':
            name = node['name']
            if name == 'enemy':
                return False
            return bool(symbol_table.get(name, 0))

        if t == 'binary_op':
            op = node['op']
            l  = eval_numeric(node['left'])
            r  = eval_numeric(node['right'])
            if op == '==': return l == r
            if op == '!=': return l != r
            if op == '>':  return l >  r
            if op == '<':  return l <  r
            if op == '>=': return l >= r
            if op == '<=': return l <= r

        if t == 'boolean':
            return node['value']

        return False

    def check_enemy_debuff(debuff_name: str) -> bool:
        """Check whether the enemy currently has a specific debuff."""
        if enemy is None:
            return False
        return any(d.name.lower() == debuff_name.lower() for d in enemy.debuffs)


    def execute_stmt(stmt: dict):
        stype = stmt.get('type')


        if stype == 'declaration':
            var    = stmt.get('name', '')
            dtype  = stmt.get('datatype', '')
            is_roll = stmt.get('is_roll', False)
            value  = stmt.get('value', {'type': 'number', 'value': 0})

            if dtype == 'bolt':
                if var == 'dmg':
                    rolls = roll_expr(value)
                    damage_rolls.extend(rolls)
                    symbol_table[var] = sum(rolls)

                elif var == 'def':
                    rolls = roll_expr(value)
                    defense_rolls.extend(rolls)
                    symbol_table[var] = sum(rolls)

                elif var == 'heal':
                    rolls = roll_expr(value)
                    heal_rolls.extend(rolls)
                    symbol_table[var] = sum(rolls)

                elif var == 'pow':
                    rolls = roll_expr(value)
                    strength_rolls.extend(rolls)
                    symbol_table[var] = sum(rolls)

                else:

                    if is_roll:
                        sides = max(1, int(eval_numeric(value)))
                        result = random.randint(1, sides)
                        symbol_table[var] = result
                    else:
                        symbol_table[var] = eval_numeric(value)

            elif dtype == 'scroll':



                debuff_name, duration = _parse_debuff_scroll(stmt, value)
                if debuff_name:
                    debuffs_out.append(EnemyDebuff(debuff_name, duration, duration if debuff_name in ('poison','burn') else 0))
                symbol_table[var] = debuff_name or ''

            elif dtype == 'flag':
                symbol_table[stmt.get('name','')] = bool(eval_numeric(value))


        elif stype == 'repeat':
            count_node = stmt.get('count')
            body       = stmt.get('body', [])
            if count_node is not None:
                count = max(0, int(eval_numeric(count_node)))
            else:
                count = 1
            for _ in range(count):
                try:
                    for body_stmt in body:
                        execute_stmt(body_stmt)
                except BreakException:
                    break


        elif stype == 'test':
            cond_node  = stmt.get('condition')
            pass_body  = stmt.get('pass', [])
            fail_body  = stmt.get('fail', [])


            condition_result = _resolve_test_condition(cond_node, stmt.get('_raw_condition', ''))

            branch = pass_body if condition_result else fail_body
            for body_stmt in branch:
                execute_stmt(body_stmt)

        elif stype == 'break':
            raise BreakException()

        elif stype == 'speak':
            pass

    def _parse_debuff_scroll(stmt: dict, value_node: dict):
        """
        Extract debuff name and turn duration from a scroll declaration.
        Syntax: scroll debuff ~ "debuff_name" + N.
        Returns (debuff_name: str, duration: int).

        The Lexer emits STRING tokens; the Parser's parse_primary falls through
        to the 'literal' branch for STRING, so strings appear as:
            {'type': 'literal', 'value': <string_content>}
        """
        def find_string(node):
            if node is None:
                return None
            ntype = node.get('type')
            if ntype == 'literal':
                return str(node.get('value', ''))
            if ntype == 'string':
                return str(node.get('value', ''))
            if ntype == 'binary_op':
                left = find_string(node['left'])
                if left is not None:
                    return left
                return find_string(node['right'])
            return None

        def find_number(node):
            if node is None:
                return 2
            ntype = node.get('type')
            if ntype == 'number':
                return max(1, int(node['value']))
            if ntype == 'binary_op':

                if node.get('op') == '+':
                    r = find_number(node['right'])
                    if r and r > 0:
                        return r
                return find_number(node['left'])
            return 2

        raw_name = find_string(value_node)


        if raw_name is None:
            m = re.search(r'scroll\s+\w+\s*~\s*["\']([a-zA-Z_]+)["\']', code, re.IGNORECASE)
            if m:
                raw_name = m.group(1)

        if raw_name is None:
            return None, 1

        name = raw_name.strip().strip('"').strip("'").lower()
        valid = {'vulnerable', 'poison', 'weakened', 'burn'}
        if name not in valid:
            return None, 1

        n_sides  = find_number(value_node)
        duration = random.randint(1, max(1, n_sides))
        return name, duration

    def _resolve_test_condition(cond_node: dict, raw: str) -> bool:
        """
        Resolve a test condition, handling 'enemy ~~ debuff' as a special case.
        Because '~~' is a FIXED_ASSIGN token (not OPERATOR), the parser only
        captures the left-hand identifier as the condition.  We detect this by
        scanning the raw code line for the pattern.
        """

        m = re.search(r'test\s+enemy\s*~~\s*([a-zA-Z_][a-zA-Z0-9_]*)', code, re.IGNORECASE)
        if m:
            debuff_name = m.group(1).lower()
            return check_enemy_debuff(debuff_name)


        return eval_condition(cond_node)


    for stmt in ast:
        execute_stmt(stmt)

    return {
        'success':       True,
        'damage':        sum(damage_rolls),
        'block':         sum(defense_rolls),
        'heal':          sum(heal_rolls),
        'strength':      sum(strength_rolls),
        'rolls':         damage_rolls,
        'defense_rolls': defense_rolls,
        'heal_rolls':    heal_rolls,
        'strength_rolls':strength_rolls,
        'debuffs':       debuffs_out,
        'symbol_table':  symbol_table,
    }



# Holds one card's name, HEROSCRIPT code snippet, energy cost, type and rarity.
@dataclass
class Card:
    """
    Represents a card in the game.
    Cards are the primary way players interact with the game.
    """
    name: str
    code: str
    energy_cost: int
    description: str
    card_type: str = "attack"
    rarity: str = "common"

    def __post_init__(self):
        if self.energy_cost < 0:
            self.energy_cost = 0
        if self.card_type not in ('attack', 'defense', 'power', 'skill', 'attack_power'):
            self.card_type = 'skill'
        if self.rarity not in ('common', 'uncommon', 'rare', 'legendary'):
            self.rarity = 'common'


        if self.card_type in ('attack', 'attack_power'):
            max_damage = self.calculate_max_damage()
            if max_damage > 0:
                self.energy_cost = self.energy_cost_from_max_damage(max_damage)
            else:

                self.energy_cost = max(1, self.energy_cost)

    def calculate_max_damage(self) -> int:
        """
        Estimate the maximum possible damage from the card code.
        Accounts for:
          - repeat N loops  (multiply body max by loop count)
          - bolt dmg ~ N*M  (NdM)
          - bolt dmg ~ N+N  (multi-die)
          - test/conditional branches (take the higher branch)
          - debuff cards get a +2 bonus per debuff (debuffs increase effective damage)
        """
        if self.card_type not in ('attack', 'attack_power'):
            return 0

        max_damage = 0


        for m in re.finditer(
                r'repeat\s+(\d+)\s*:\s*\n\s+bolt\s+dmg\s*~\s*([^\.\n]+)',
                self.code, re.IGNORECASE):
            repeat_count = int(m.group(1))
            expr         = m.group(2).strip()
            max_damage  += repeat_count * self._parse_max_damage_expr(expr)


        for m in re.finditer(r'bolt\s+dmg\s*~\s*([^\.\n]+)', self.code, re.IGNORECASE):
            start      = m.start()
            line_start = self.code.rfind('\n', 0, start) + 1
            prefix     = self.code[line_start:start]
            if prefix.strip() == '' and prefix != '':
                continue
            expr       = m.group(1).strip()
            max_damage += self._parse_max_damage_expr(expr)


        for m in re.finditer(
                r'test\s+enemy\s*~~\s*\w+\s*:\s*\n\s+bolt\s+dmg\s*~\s*([^\.\n]+)',
                self.code, re.IGNORECASE):
            expr       = m.group(1).strip()
            max_damage = max(max_damage, self._parse_max_damage_expr(expr))


        debuff_count = len(re.findall(r'scroll\s+debuff\s*~', self.code, re.IGNORECASE))
        max_damage  += debuff_count * 3

        return max(max_damage, 1)

    def _parse_max_damage_expr(self, expr: str) -> int:
        """
        Return the maximum possible roll value for a dice expression.
          N       → 1dN  → max N
          N * M   → NdM  → max N*M
          N + M   → 2-addend: treat as N dice of M sides → max N*M
          N+N+N.. → 3+ addends: one die per addend, max = sum
        """
        expr = expr.strip()


        m = re.fullmatch(r'(\d+)\s*\*\s*(\d+)', expr)
        if m:
            return int(m.group(1)) * int(m.group(2))

        parts = [p.strip() for p in expr.split('+') if p.strip()]

        if len(parts) == 1:
            try:
                return int(parts[0])
            except ValueError:
                pass
            dm = re.fullmatch(r'(\d*)d(\d+)', parts[0], re.IGNORECASE)
            if dm:
                c = int(dm.group(1)) if dm.group(1) else 1
                return c * int(dm.group(2))
            return 0

        if len(parts) == 2:
            try:
                n, m2 = int(parts[0]), int(parts[1])
                return n * m2
            except ValueError:
                pass


        total = 0
        for p in parts:
            try:
                total += int(p)
            except ValueError:
                dm = re.fullmatch(r'(\d*)d(\d+)', p, re.IGNORECASE)
                if dm:
                    c = int(dm.group(1)) if dm.group(1) else 1
                    total += c * int(dm.group(2))
        return total

    def energy_cost_from_max_damage(self, max_damage: int) -> int:
        """
        Map max damage to energy cost.  Hard cap of 8.
        Thresholds:
          1-4   → 1E   (starter jabs)
          5-8   → 2E   (basic strike)
          9-14  → 3E   (standard attacks)
          15-20 → 4E   (heavy hits)
          21-28 → 5E   (power attacks)
          29-36 → 6E   (elite moves)
          37-46 → 7E   (legendary tier)
          47+   → 8E   (absolute maximum)
        """
        if max_damage <=  4: return 1
        if max_damage <=  8: return 2
        if max_damage <= 14: return 3
        if max_damage <= 20: return 4
        if max_damage <= 28: return 5
        if max_damage <= 36: return 6
        if max_damage <= 46: return 7
        return 8

    def __repr__(self):
        return f"Card({self.name}, {self.energy_cost}E, {self.card_type})"

    def execute(self) -> Dict[str, Any]:
        """Execute the card's code and return results."""
        return execute_card_code(self.code)

    def get_tooltip(self) -> str:
        """Get a tooltip description of the card."""
        return f"{self.name} ({self.energy_cost}E)\n{self.description}\n{self.card_type.title()}"

    def get_color(self) -> str:
        """Get the display color for this card based on rarity and type."""
        rarity_colors = {
            'common': '#4A4A4A',
            'uncommon': '#2E7D32',
            'rare': '#1565C0',
            'legendary': '#E65100',
        }
        type_colors = {
            'attack': '#8B0000',
            'defense': '#1B5E20',
            'power': '#4A148C',
            'skill': '#01579B',
            'attack_power': '#B71C1C',
        }

        if self.rarity in ('rare', 'legendary'):
            return rarity_colors.get(self.rarity, '#4A4A4A')
        return type_colors.get(self.card_type, '#4A4A4A')

# All playable cards, grouped by unlock tier.
# STARTER always available; TIER1 from floor 1; TIER2 floor 3; TIER3 floor 6.
class CardLibrary:
    """
    Library of all available cards in the game.
    Organised by tier. Every card's code follows the HEROSCRIPT cheat sheet:
      bolt dmg  ~ N.          → roll 1dN damage
      bolt dmg  ~ N * M.      → roll N dice of M sides  (NdM)
      bolt dmg  ~ N + N + N.  → roll one die per addend (each die = 1dN)
      bolt def  ~ N.          → roll 1dN block
      bolt heal ~ N.          → roll 1dN healing
      bolt pow  ~ N.          → gain N strength
      repeat K:\n    bolt dmg ~ N.\nend.   → barrage: roll K times
      scroll debuff ~ "name" + N.          → apply debuff for 1dN turns
      test enemy ~~ debuff:\n  bolt dmg ~ N * M.\nfail:\n  bolt dmg ~ N.\nclose.
    """


    STARTER_CARDS = [
        Card("Quick Strike",
             "bolt dmg ~ 4.",
             1, "Roll 1d4 damage", "attack", "common"),

        Card("Poke",
             "bolt dmg ~ 3.",
             1, "Roll 1d3 damage", "attack", "common"),

        Card("Tap",
             "bolt dmg ~ 5.",
             1, "Roll 1d5 damage", "attack", "common"),

        Card("Minor Block",
             "bolt def ~ 4.",
             1, "Roll 1d4 block", "defense", "common"),

        Card("Guard",
             "bolt def ~ 5.",
             1, "Roll 1d5 block", "defense", "common"),

        Card("Minor Heal",
             "bolt heal ~ 5.",
             1, "Roll 1d5 healing", "skill", "common"),
    ]


    TIER1_CARDS = [

        Card("Standard Strike",
             "bolt dmg ~ 6.",
             2, "Roll 1d6 damage", "attack", "common"),

        Card("Double Tap",
             "bolt dmg ~ 3 + 3.",
             2, "Roll 2d3 damage (2 dice, 3 sides each)", "attack", "uncommon"),


        Card("Standard Shield",
             "bolt def ~ 6.",
             2, "Roll 1d6 block", "defense", "common"),


        Card("Minor Recovery",
             "bolt heal ~ 8.",
             2, "Roll 1d8 healing", "skill", "common"),

        Card("Prepare",
             "bolt pow ~ 1.",
             1, "Gain 1 strength", "power", "common"),


        Card("Rapid Jabs",
             "repeat 3:\n    bolt dmg ~ 3.\nend.",
             2, "Hit 3 times, each roll 1d3 (max 9)", "attack", "uncommon"),


        Card("Expose Weakness",
             'bolt dmg ~ 4.\nscroll debuff ~ "vulnerable" + 2.',
             2, "Deal 1d4 damage, apply Vulnerable 1d2 turns", "attack", "uncommon"),
    ]


    TIER2_CARDS = [

        Card("Heavy Bolt",
             "bolt dmg ~ 10.",
             3, "Roll 1d10 damage", "attack", "uncommon"),

        Card("Triple Strike",
             "bolt dmg ~ 2 + 2 + 2.",
             2, "Roll 3d2 damage (3 dice, 2 sides each)", "attack", "uncommon"),

        Card("Power Strike",
             "bolt dmg ~ 6 * 4.",
             5, "Roll 6d4 damage (max 24)", "attack", "uncommon"),


        Card("Reinforce",
             "bolt def ~ 10.",
             3, "Roll 1d10 block", "defense", "uncommon"),

        Card("Fortify",
             "bolt def ~ 4 * 4.",
             4, "Roll 4d4 block (max 16)", "defense", "uncommon"),


        Card("First Aid",
             "bolt heal ~ 12.",
             3, "Roll 1d12 healing", "skill", "uncommon"),

        Card("Strength Up",
             "bolt pow ~ 2.",
             2, "Gain 2 strength", "power", "uncommon"),

        Card("Power Surge",
             "bolt pow ~ 3.",
             3, "Gain 3 strength", "power", "rare"),


        Card("Flurry",
             "repeat 4:\n    bolt dmg ~ 3.\nend.",
             3, "Hit 4 times, each roll 1d3 (max 12)", "attack", "uncommon"),

        Card("Salvo",
             "repeat 3:\n    bolt dmg ~ 2 * 2.\nend.",
             3, "Hit 3 times, each roll 2d2 (max 12)", "attack", "uncommon"),


        Card("Poison Dart",
             'bolt dmg ~ 3.\nscroll debuff ~ "poison" + 3.',
             3, "Deal 1d3 damage, apply Poison 1d3 turns", "attack", "uncommon"),

        Card("Searing Strike",
             'bolt dmg ~ 5.\nscroll debuff ~ "burn" + 2.',
             3, "Deal 1d5 damage, apply Burn 1d2 turns", "attack", "uncommon"),


        Card("Exploit",
             'test enemy ~~ vulnerable:\n    bolt dmg ~ 2 * 6.\nfail:\n    bolt dmg ~ 6.\nclose.',
             3, "If enemy Vulnerable: 2d6 damage; else 1d6", "attack", "uncommon"),
    ]


    TIER3_CARDS = [

        Card("Heavy Strike",
             "bolt dmg ~ 14.",
             4, "Roll 1d14 damage", "attack", "rare"),

        Card("Critical Hit",
             "bolt dmg ~ 3 * 8.",
             4, "Roll 3d8 damage (max 24)", "attack", "rare"),

        Card("Mega Strike",
             "bolt dmg ~ 2 * 12.",
             4, "Roll 2d12 damage (max 24)", "attack", "rare"),

        Card("Devastate",
             "bolt dmg ~ 5 * 6.",
             5, "Roll 5d6 damage (max 30)", "attack", "legendary"),


        Card("Iron Wall",
             "bolt def ~ 14.",
             4, "Roll 1d14 block", "defense", "rare"),

        Card("Mega Shield",
             "bolt def ~ 2 * 12.",
             4, "Roll 2d12 block (max 24)", "defense", "rare"),

        Card("Ultimate Defense",
             "bolt def ~ 3 * 8.",
             4, "Roll 3d8 block (max 24)", "defense", "legendary"),


        Card("Grand Heal",
             "bolt heal ~ 20.",
             4, "Roll 1d20 healing", "skill", "rare"),

        Card("Surge",
             "bolt pow ~ 4.",
             4, "Gain 4 strength", "power", "rare"),


        Card("Chain Lightning",
             "repeat 5:\n    bolt dmg ~ 4.\nend.",
             4, "Hit 5 times, each roll 1d4 (max 20)", "attack", "rare"),

        Card("Bullet Storm",
             "repeat 6:\n    bolt dmg ~ 3.\nend.",
             4, "Hit 6 times, each roll 1d3 (max 18)", "attack", "rare"),

        Card("Storm Barrage",
             "repeat 4:\n    bolt dmg ~ 2 * 3.\nend.",
             5, "Hit 4 times, each roll 2d3 (max 24)", "attack", "rare"),


        Card("Venom Blade",
             'bolt dmg ~ 8.\nscroll debuff ~ "poison" + 4.',
             4, "Deal 1d8 damage, apply Poison 1d4 turns", "attack", "rare"),

        Card("Inferno Strike",
             'bolt dmg ~ 2 * 5.\nscroll debuff ~ "burn" + 3.',
             4, "Deal 2d5 damage, apply Burn 1d3 turns", "attack", "rare"),

        Card("Crippling Blow",
             'bolt dmg ~ 10.\nscroll debuff ~ "weakened" + 3.',
             4, "Deal 1d10 damage, apply Weakened 1d3 turns", "attack", "rare"),


        Card("Punish",
             'test enemy ~~ vulnerable:\n    bolt dmg ~ 4 * 5.\nfail:\n    bolt dmg ~ 2 * 5.\nclose.',
             4, "If Vulnerable: 4d5 damage; else 2d5", "attack", "rare"),

        Card("Toxic Finish",
             'test enemy ~~ poison:\n    bolt dmg ~ 3 * 8.\nfail:\n    bolt dmg ~ 8.\nclose.',
             4, "If Poisoned: 3d8 damage; else 1d8", "attack", "rare"),

        Card("Execute",
             'test enemy ~~ weakened:\n    bolt dmg ~ 5 * 6.\nfail:\n    bolt dmg ~ 12.\nclose.',
             5, "If Weakened: 5d6 damage; else 1d12", "attack", "legendary"),
    ]


    SPECIAL_CARDS = [
        Card("Meteor Strike",
             "bolt dmg ~ 20.",
             6, "Roll 1d20 damage", "attack", "legendary"),

        Card("Divine Shield",
             "bolt def ~ 20.",
             6, "Roll 1d20 block", "defense", "legendary"),

        Card("Phoenix Rising",
             "bolt heal ~ 15.\nbolt pow ~ 2.",
             5, "Heal 1d15 HP, gain 2 strength", "power", "legendary"),

        Card("Loop Jab",
             "bolt dmg ~ 3 + 3 + 3 + 3.",
             3, "Roll 4d3 damage (4 dice, 3 sides each)", "attack", "rare"),

        Card("Barrage",
             "repeat 5:\n    bolt dmg ~ 2.\nend.",
             3, "Hit 5 times, each roll 1d2 (max 10)", "attack", "rare"),


        Card("Plague Touch",
             'bolt dmg ~ 5.\nscroll debuff ~ "poison" + 5.',
             4, "Deal 1d5 damage, apply Poison 1d5 turns", "attack", "rare"),

        Card("Apocalyptic Barrage",
             "repeat 8:\n    bolt dmg ~ 4.\nend.",
             6, "Hit 8 times, each roll 1d4 (max 32)", "attack", "legendary"),

        Card("Burning Cyclone",
             'repeat 4:\n    bolt dmg ~ 3.\nend.\nscroll debuff ~ "burn" + 4.',
             5, "Hit 4 times 1d3 each + Burn 1d4 turns", "attack", "legendary"),

        Card("Vulnerability Loop",
             'scroll debuff ~ "vulnerable" + 3.\nrepeat 3:\n    bolt dmg ~ 5.\nend.',
             5, "Apply Vulnerable 1d3 turns, then hit 3×1d5", "attack", "legendary"),

        Card("Overkill",
             'test enemy ~~ vulnerable:\n    bolt dmg ~ 6 * 6.\nfail:\n    bolt dmg ~ 3 * 6.\nclose.',
             6, "If Vulnerable: 6d6 damage; else 3d6", "attack", "legendary"),
    ]

    @classmethod
    def get_cards_for_floor(cls, floor: int) -> List[Card]:
        cards = list(cls.STARTER_CARDS) + list(cls.TIER1_CARDS)
        if floor >= 3:
            cards.extend(cls.TIER2_CARDS)
        if floor >= 6:
            cards.extend(cls.TIER3_CARDS)
        return cards

    @classmethod
    def get_random_card(cls, floor: int) -> Card:
        return random.choice(cls.get_cards_for_floor(floor))

    @classmethod
    def get_reward_cards(cls, floor: int, count: int = 3) -> List[Card]:
        available = [c for c in cls.get_cards_for_floor(floor)
                     if c.rarity != 'legendary' or floor > 4]
        return random.sample(available, min(count, len(available)))



# Passive item that permanently modifies player stats while equipped.
@dataclass
class Relic:
    """
    Represents a relic - a passive item that provides bonuses.
    Players can equip up to 3 relics at a time.
    """
    name: str
    description: str
    effect_type: str
    effect_value: int
    rarity: str = "common"

    def __repr__(self):
        return f"Relic({self.name})"

    def apply(self, player: 'Player'):
        """Apply the relic's effect to the player."""
        if self.effect_type == 'energy':
            player.max_energy += self.effect_value
            player.energy += self.effect_value
        elif self.effect_type == 'draw':
            player.draw_count += self.effect_value
        elif self.effect_type == 'heal_start':
            player.heal_at_combat_start += self.effect_value

    def remove(self, player: 'Player'):
        """Remove the relic's effect from the player."""
        if self.effect_type == 'energy':
            player.max_energy = max(0, player.max_energy - self.effect_value)
            player.energy = min(player.energy, player.max_energy)
        elif self.effect_type == 'draw':
            player.draw_count = max(0, player.draw_count - self.effect_value)
        elif self.effect_type == 'heal_start':
            player.heal_at_combat_start = max(0, player.heal_at_combat_start - self.effect_value)

    def get_bonus(self, stat: str) -> int:
        """Get a bonus for a specific stat."""
        if stat == 'damage' and self.effect_type == 'damage':
            return self.effect_value
        if stat == 'block' and self.effect_type == 'defense':
            return self.effect_value
        return 0

# Full catalogue of relics; weighted random selection scales with floor depth.
class RelicLibrary:
    """
    Library of all available relics.
    """

    RELICS = [

        Relic("Red Idol",       "+1 damage per attack",     "damage",     1, "common"),
        Relic("Golden Shield",  "+1 block per defense",     "defense",    1, "common"),
        Relic("Iron Knuckle",   "+1 damage per attack",     "damage",     1, "common"),
        Relic("Leather Wrap",   "+1 block per defense",     "defense",    1, "common"),
        Relic("Canteen",        "Heal 3 HP at combat start","heal_start", 3, "common"),
        Relic("Lucky Coin",     "Draw +1 card per turn",    "draw",       1, "common"),


        Relic("Silver Boots",   "+1 energy per turn",       "energy",     1, "uncommon"),
        Relic("Sword Charm",    "+2 damage per attack",     "damage",     2, "uncommon"),
        Relic("Tower Shield",   "+2 block per defense",     "defense",    2, "uncommon"),
        Relic("Arcane Eye",     "Draw +1 card per turn",    "draw",       1, "uncommon"),
        Relic("Phoenix Feather","Heal 5 HP at combat start","heal_start", 5, "uncommon"),
        Relic("Battle Drum",    "+2 damage per attack",     "damage",     2, "uncommon"),
        Relic("Crystal Lens",   "+2 energy per turn",       "energy",     2, "uncommon"),
        Relic("Thorn Band",     "+1 block per defense",     "defense",    1, "uncommon"),
        Relic("Swift Boots",    "Draw +1 card per turn",    "draw",       1, "uncommon"),
        Relic("Bandage Roll",   "Heal 8 HP at combat start","heal_start", 8, "uncommon"),


        Relic("War Horn",       "+3 damage per attack",     "damage",     3, "rare"),
        Relic("Paladin Helm",   "+3 block per defense",     "defense",    3, "rare"),
        Relic("Elixir of Life", "Heal 10 HP at combat start","heal_start",10, "rare"),
        Relic("Battle Axe",     "+4 damage per attack",     "damage",     4, "rare"),
        Relic("Fortress Wall",  "+4 block per defense",     "defense",    4, "rare"),
        Relic("Mana Prism",     "+2 energy per turn",       "energy",     2, "rare"),
        Relic("Scholar's Tome", "Draw +2 cards per turn",   "draw",       2, "rare"),
        Relic("Blood Stone",    "Heal 12 HP at combat start","heal_start",12, "rare"),
        Relic("Rage Sigil",     "+3 damage per attack",     "damage",     3, "rare"),
        Relic("Iron Bulwark",   "+3 block per defense",     "defense",    3, "rare"),
        Relic("Runner's Charm", "+1 energy per turn",       "energy",     1, "rare"),


        Relic("Heart of the Mountain", "+2 energy per turn",      "energy",     2, "legendary"),
        Relic("Dragon Scale",          "+5 damage per attack",    "damage",     5, "legendary"),
        Relic("Ancient Tome",          "Draw +2 cards per turn",  "draw",       2, "legendary"),
        Relic("Titan's Gauntlet",      "+6 damage per attack",    "damage",     6, "legendary"),
        Relic("Aegis of Eternity",     "+6 block per defense",    "defense",    6, "legendary"),
        Relic("Philosopher's Stone",   "+3 energy per turn",      "energy",     3, "legendary"),
        Relic("Grimoire of Souls",     "Draw +3 cards per turn",  "draw",       3, "legendary"),
        Relic("Ambrosia Flask",        "Heal 20 HP at combat start","heal_start",20,"legendary"),
    ]

    @classmethod
    def get_random_relic(cls, rarity: str = None, floor: int = 0) -> Relic:
        """Get a random relic, optionally of a specific rarity and floor gating."""
        if rarity:
            available = [r for r in cls.RELICS if r.rarity == rarity]
            return random.choice(available) if available else cls.RELICS[0]


        if floor <= 4:
            weights = {'common': 60, 'uncommon': 30, 'rare': 10, 'legendary': 0}
        elif floor <= 9:
            weights = {'common': 50, 'uncommon': 30, 'rare': 15, 'legendary': 5}
        else:
            weights = {'common': 35, 'uncommon': 30, 'rare': 20, 'legendary': 15}

        available = []
        for r in cls.RELICS:
            available.extend([r] * weights.get(r.rarity, 10))

        return random.choice(available) if available else cls.RELICS[0]

    @classmethod
    def get_relics_by_rarity(cls, rarity: str) -> List[Relic]:
        """Get all relics of a specific rarity."""
        return [r for r in cls.RELICS if r.rarity == rarity]



# Crafting ingredient dropped after combat; combined with cards to upgrade them.
@dataclass
class TraceElement:
    """
    Represents a trace element dropped after combat.
    Can be combined with protocols (cards) to create enhanced versions.
    """
    name: str
    rarity: str
    tag: str
    effect_type: str
    effect_value: int
    description: str

    def __repr__(self):
        return f"TraceElement({self.name})"

# Defines which card + trace element produce which upgraded card.
@dataclass
class CraftingRecipe:
    """
    Represents a crafting recipe combining a card with a trace element.
    """
    original_card_name: str
    ingredient_name: str
    result_card: Card
    description: str
    rarity: str

    def can_craft(self, card: Card, ingredient: TraceElement) -> bool:
        """Check if this recipe can be crafted."""
        return card.name == self.original_card_name and ingredient.name == self.ingredient_name

    def __repr__(self):
        return f"Recipe({self.original_card_name} + {self.ingredient_name})"

# Pool of all trace elements; rarity weighting shifts toward rare at high floors.
class TraceElementLibrary:
    """
    Library of all available trace elements for crafting.
    """

    ELEMENTS = [

        TraceElement("Chromatic Pulse", "common", "fire", "damage_boost", 2, "+2 damage to card"),
        TraceElement("Harmonic Echo", "common", "frost", "block_boost", 2, "+2 block to card"),
        TraceElement("Recursive Logic", "common", "meta", "energy_reduction", 1, "-1 energy cost"),
        TraceElement("Data Fragment", "common", "void", "damage_boost", 1, "+1 damage"),
        TraceElement("Temporal Shard", "common", "time", "special", 1, "Delays effect 1 turn"),
        TraceElement("Void Resonance", "common", "void", "block_boost", 1, "+1 block"),


        TraceElement("Void Shard", "uncommon", "void", "special", 2, "Effect carries to next turn"),
        TraceElement("Temporal Lock", "uncommon", "time", "special", 1, "Enemy loses 1 action next turn"),
        TraceElement("Quantum Foam", "uncommon", "meta", "special", 1, "50% chance to double effect"),
        TraceElement("Inferno Core", "uncommon", "fire", "damage_boost", 4, "+4 damage"),
        TraceElement("Frost Nucleus", "uncommon", "frost", "block_boost", 4, "+4 block"),
        TraceElement("Metal Shard", "uncommon", "metal", "block_boost", 3, "+3 block"),
        TraceElement("Essence Extractor", "uncommon", "void", "energy_reduction", 2, "-2 energy cost"),
        TraceElement("Prismatic Shard", "uncommon", "fire", "damage_boost", 3, "+3 damage"),


        TraceElement("Insight Node", "rare", "meta", "special", 1, "Draw 1 card when played"),
        TraceElement("Resonance Core", "rare", "meta", "special", 2, "Double effect once per combat"),
        TraceElement("Memory Trace", "rare", "meta", "special", 1, "Copy to hand next turn"),
        TraceElement("Cascade Node", "rare", "fire", "special", 1, "Chain effect to next card"),
        TraceElement("Phoenix Essence", "rare", "fire", "damage_boost", 6, "+6 damage, burn effect added"),
        TraceElement("Glacial Essence", "rare", "frost", "block_boost", 6, "+6 block, freeze added"),
        TraceElement("Metallic Essence", "rare", "metal", "block_boost", 5, "+5 block, reflect damage"),
        TraceElement("Void Essence", "rare", "void", "special", 2, "Nullify enemy effect"),
        TraceElement("Chrono Essence", "rare", "time", "special", 1, "Extra turn 25% chance"),
        TraceElement("Amplifier Lattice", "rare", "meta", "damage_boost", 8, "+8 damage"),
        TraceElement("Stabilizer Matrix", "rare", "meta", "block_boost", 8, "+8 block"),
    ]

    @classmethod
    def get_random_element(cls, rarity: str = None, floor: int = 0) -> TraceElement:
        """Get a random trace element."""
        if rarity:
            available = [e for e in cls.ELEMENTS if e.rarity == rarity]
        else:

            common_weight = max(0, 50 - floor * 3)
            uncommon_weight = 30 + floor * 2
            rare_weight = max(5, floor * 2)

            available = []
            for e in cls.ELEMENTS:
                if e.rarity == "common":
                    available.extend([e] * common_weight)
                elif e.rarity == "uncommon":
                    available.extend([e] * uncommon_weight)
                elif e.rarity == "rare":
                    available.extend([e] * rare_weight)

        return random.choice(available) if available else cls.ELEMENTS[0]

    @classmethod
    def get_elements_by_rarity(cls, rarity: str) -> List[TraceElement]:
        """Get all elements of a specific rarity."""
        return [e for e in cls.ELEMENTS if e.rarity == rarity]

# 30+ recipes mapping (card name, ingredient name) → upgraded Card result.
class CraftingRecipeLibrary:
    """
    Library of all available crafting recipes.30+ recipes combining cards with trace elements.
    """

    @staticmethod
    def _build_recipes() -> List[CraftingRecipe]:
        """Build the complete recipe list (30+ recipes)."""
        recipes = [

            CraftingRecipe(
                "Quick Strike",
                "Chromatic Pulse",
                Card("Prismatic Blow", "bolt dmg ~ 6.", 1, "+1 damage, colorful", "attack", "uncommon"),
                "Quick Strike enhanced with chromatic energy",
                "common"
            ),
            CraftingRecipe(
                "Quick Strike",
                "Inferno Core",
                Card("Flame Strike", "bolt dmg ~ 9.", 1, "+5 damage, ignites target", "attack", "uncommon"),
                "Quick Strike burning with inferno",
                "uncommon"
            ),
            CraftingRecipe(
                "Standard Strike",
                "Void Shard",
                Card("Persistent Strike", "bolt dmg ~ 7.", 2, "Damage carries over", "attack", "uncommon"),
                "Standard Strike with lingering void damage",
                "uncommon"
            ),
            CraftingRecipe(
                "Standard Strike",
                "Prismatic Shard",
                Card("Power Burst", "bolt dmg ~ 9.", 2, "+3 damage boost", "attack", "uncommon"),
                "Standard Strike amplified with prismatic energy",
                "uncommon"
            ),
            CraftingRecipe(
                "Heavy Bolt",
                "Phoenix Essence",
                Card("Inferno Blast", "bolt dmg ~ 16.", 3, "+6 damage, burn added", "attack", "rare"),
                "Heavy Bolt wreathed in phoenix flames",
                "rare"
            ),
            CraftingRecipe(
                "Heavy Bolt",
                "Void Essence",
                Card("Void Strike", "bolt dmg ~ 15.", 3, "+5 damage", "attack", "rare"),
                "Heavy Bolt channeling void energy",
                "rare"
            ),


            CraftingRecipe(
                "Minor Block",
                "Harmonic Echo",
                Card("Harmonic Shield", "bolt def ~ 6.", 1, "+2 block", "defense", "uncommon"),
                "Block reinforced with echoing harmonics",
                "common"
            ),
            CraftingRecipe(
                "Minor Block",
                "Insight Node",
                Card("Sentinel Recall", "bolt def ~ 5.", 1, "+1 block, draw card", "defense", "uncommon"),
                "Block with recall ability",
                "uncommon"
            ),
            CraftingRecipe(
                "Standard Shield",
                "Glacial Essence",
                Card("Frozen Fortress", "bolt def ~ 16.", 2, "+6 block, freeze added", "defense", "rare"),
                "Shield crystallized with glacial essence",
                "rare"
            ),
            CraftingRecipe(
                "Standard Shield",
                "Metallic Essence",
                Card("Iron Bulwark", "bolt def ~ 15.", 2, "+5 block, reflect", "defense", "rare"),
                "Shield reinforced with metallic power",
                "rare"
            ),
            CraftingRecipe(
                "Guard",
                "Frost Nucleus",
                Card("Crystal Guard", "bolt def ~ 8.", 1, "+3 block", "defense", "uncommon"),
                "Guard hardened by frost magic",
                "uncommon"
            ),


            CraftingRecipe(
                "Quick Strike",
                "Recursive Logic",
                Card("Efficient Strike", "bolt dmg ~ 4.", 0, "Free card!", "attack", "rare"),
                "Quick Strike optimized for efficiency",
                "uncommon"
            ),
            CraftingRecipe(
                "Minor Block",
                "Essence Extractor",
                Card("Fortified Stance", "bolt def ~ 4.", 0, "Free defense", "defense", "uncommon"),
                "Block costing no energy",
                "uncommon"
            ),
            CraftingRecipe(
                "Prepare",
                "Quantum Foam",
                Card("Quantum Buff", "bolt pow ~ 1.", 1, "50% chance to double", "power", "uncommon"),
                "Prepare enhanced with quantum probability",
                "uncommon"
            ),
            CraftingRecipe(
                "Minor Heal",
                "Harmonic Echo",
                Card("Soothing Resonance", "bolt heal ~ 7.", 1, "+2 healing", "skill", "uncommon"),
                "Healing amplified through harmony",
                "uncommon"
            ),


            CraftingRecipe(
                "Triple Strike",
                "Cascade Node",
                Card("Cascade Barrage", "bolt dmg ~ 2 + 2 + 2. bolt pow ~ 1.", 2, "Triple hit + strength", "attack_power", "rare"),
                "Triple Strike with cascading power",
                "rare"
            ),
            CraftingRecipe(
                "Loop Jab",
                "Resonance Core",
                Card("Resonant Loop", "bolt dmg ~ 3 + 3 +3 + 3.", 3, "Doubled effect once", "attack", "rare"),
                "Loop Jab with resonant doubling",
                "rare"
            ),


            CraftingRecipe(
                "Meteor Strike",
                "Amplifier Lattice",
                Card("Apocalyptic Impact", "bolt dmg ~ 28.", 6, "+8 damage nuclear option", "attack", "legendary"),
                "Meteor amplified to apocalyptic levels",
                "rare"
            ),
            CraftingRecipe(
                "Divine Shield",
                "Stabilizer Matrix",
                Card("Absolute Fortress", "bolt def ~ 28.", 6, "+8 block unbreakable", "defense", "legendary"),
                "Shield stabilized to perfection",
                "rare"
            ),


            CraftingRecipe(
                "Prepare",
                "Inferno Core",
                Card("Infernal Surge", "bolt pow ~ 4.", 1, "+3 strength with fire", "power", "uncommon"),
                "Preparation infused with fire",
                "uncommon"
            ),
            CraftingRecipe(
                "Strength Up",
                "Temporal Lock",
                Card("Temporal Surge", "bolt pow ~ 3.", 2, "+1 strength, enemy lose action", "power", "uncommon"),
                "Strength amplified with temporal power",
                "uncommon"
            ),
            CraftingRecipe(
                "Power Surge",
                "Void Essence",
                Card("Void Ascension", "bolt pow ~ 6.", 3, "Void-powered strength", "power", "rare"),
                "Power Surge channeling void energy",
                "rare"
            ),


            CraftingRecipe(
                "Quick Strike",
                "Essence Extractor",
                Card("Efficient Jab", "bolt dmg ~ 4.", 0, "Free damage", "attack", "rare"),
                "Strike costing no energy",
                "uncommon"
            ),
            CraftingRecipe(
                "Minor Block",
                "Recursive Logic",
                Card("Self-Reinforcing Ward", "bolt def ~ 4.", 0, "Free defense", "defense", "uncommon"),
                "Defense that refunds energy",
                "uncommon"
            ),


            CraftingRecipe(
                "Minor Heal",
                "Insight Node",
                Card("Healing Clarity", "bolt heal ~ 5.", 1, "Heal and draw", "skill", "uncommon"),
                "Healing with clarity boost",
                "uncommon"
            ),
            CraftingRecipe(
                "Grand Heal",
                "Memory Trace",
                Card("Eternal Healing", "bolt heal ~ 20.", 4, "Repeats next turn", "skill", "rare"),
                "Heal that echoes across turns",
                "rare"
            ),


            CraftingRecipe(
                "Barrage",
                "Quantum Foam",
                Card("Quantum Volley", "bolt dmg ~ 2 + 2 + 2 + 2 + 2.", 4, "50% to double all", "attack", "rare"),
                "Barrage with quantum probability",
                "rare"
            ),
            CraftingRecipe(
                "Critical Hit",
                "Amplifier Lattice",
                Card("Devastating Combo", "bolt dmg ~ 8 + 8 + 8.", 4, "+8 to all hits", "attack", "rare"),
                "Critical Hit amplified to devastating levels",
                "rare"
            ),
            CraftingRecipe(
                "Phoenix Rising",
                "Phoenix Essence",
                Card("Phoenix Reborn", "bolt dmg ~ 6. bolt heal ~ 20. bolt pow ~ 3.", 5, "Enhanced phoenix", "attack_power", "legendary"),
                "Phoenix power doubled with pure essence",
                "legendary"
            ),
        ]

        return recipes

    RECIPES = _build_recipes()

    @classmethod
    def find_recipe(cls, card: Card, element: TraceElement) -> Optional[CraftingRecipe]:
        """Find a recipe that matches the card and element."""
        for recipe in cls.RECIPES:
            if recipe.can_craft(card, element):
                return recipe
        return None

    @classmethod
    def get_recipes_for_card(cls, card: Card) -> List[CraftingRecipe]:
        """Get all recipes that work with a specific card."""
        return [r for r in cls.RECIPES if r.original_card_name == card.name]

    @classmethod
    def get_recipes_for_element(cls, element: TraceElement) -> List[CraftingRecipe]:
        """Get all recipes that use a specific element."""
        return [r for r in cls.RECIPES if r.ingredient_name == element.name]

    @classmethod
    def craft(cls, card: Card, element: TraceElement) -> Optional[Card]:
        """Craft a card with an element, returning the new card."""
        recipe = cls.find_recipe(card, element)
        if recipe:
            return recipe.result_card
        return None



# Describes one playable class: base stats, starting deck, and passive ability.
@dataclass
class CharacterClass:
    """
    Represents a playable character class.
    Each class has unique starting cards, HP, and passive abilities.
    """
    name: str
    display_name: str
    title: str
    max_hp: int
    base_energy: int
    starting_strength: int
    starting_cards: List[Card]
    passive_ability: str
    passive_description: str
    color: str

    def __repr__(self):
        return f"Class({self.name})"

# Registry of all 7 playable classes; keyed by class name string.
class CharacterClassLibrary:
    """
    Library of all playable character classes.
    """

    CLASSES = {
        "Ironclad": CharacterClass(
            name="Ironclad",
            display_name="IRONCLAD",
            title="The Stalwart Warrior",
            max_hp=90,
            base_energy=8,
            starting_strength=3,
            starting_cards=[
                Card("Bash", "bolt dmg ~ 8.", 2, "Roll 1d8 damage", "attack", "common"),
                Card("Strike", "bolt dmg ~ 6.", 1, "Roll 1d6 damage", "attack", "common"),
                Card("Shield Up", "bolt def ~ 8.", 1, "Roll 1d8 block", "defense", "common"),
                Card("Cleave", "bolt dmg ~ 4 + 4.", 1, "Roll 2d4 damage", "attack", "common"),
            ],
            passive_ability="REGENERATION",
            passive_description="At the end of each turn, heal 1 HP.",
            color="#802020"
        ),

        "Silent": CharacterClass(
            name="Silent",
            display_name="SILENT",
            title="The Swift Assassin",
            max_hp=75,
            base_energy=8,
            starting_strength=2,
            starting_cards=[
                Card("Strike", "bolt dmg ~ 4.", 1, "Roll 1d4 damage", "attack", "common"),
                Card("Slice", "bolt dmg ~ 3 + 3.", 1, "Roll 2d3 damage", "attack", "common"),
                Card("Shiv", "bolt dmg ~ 2.", 0, "Roll 1d2 damage", "attack", "common"),
                Card("Dodge", "bolt def ~ 6.", 1, "Roll 1d6 block", "defense", "common"),
            ],
            passive_ability="EVASION",
            passive_description="After playing an attack, gain 1 temporary block.",
            color="#208020"
        ),

        "Defect": CharacterClass(
            name="Defect",
            display_name="DEFECT",
            title="The Arcane Wielder",
            max_hp=70,
            base_energy=8,
            starting_strength=1,
            starting_cards=[
                Card("Zap", "bolt dmg ~ 5.", 1, "Roll 1d5 damage", "attack", "common"),
                Card("Orb Charge", "bolt pow ~ 2.", 1, "Gain 2 strength", "power", "uncommon"),
                Card("Barrier", "bolt def ~ 7.", 1, "Roll 1d7 block", "defense", "common"),
                Card("Spark", "bolt dmg ~ 3.", 1, "Roll 1d3 damage", "attack", "common"),
            ],
            passive_ability="ENERGY Surge",
            passive_description="At the start of each turn, if no attack was played last turn, gain 1 extra energy.",
            color="#204080"
        ),

        "Watcher": CharacterClass(
            name="Watcher",
            display_name="WATCHER",
            title="The Disciplined Monk",
            max_hp=72,
            base_energy=8,
            starting_strength=1,
            starting_cards=[
                Card("Strike", "bolt dmg ~ 5.", 1, "Roll 1d5 damage", "attack", "common"),
                Card("Calm", "bolt def ~ 8.", 1, "Roll 1d8 block", "defense", "common"),
                Card("Stance Shift", "bolt pow ~ 3.", 2, "Gain 3 strength", "power", "uncommon"),
                Card("Snipe", "bolt dmg ~ 6.", 2, "Roll 1d6 damage", "attack", "common"),
            ],
            passive_ability="DISCIPLINE",
            passive_description="Gain +1 strength on odd-numbered turns.",
            color="#704080"
        ),

        "Glass Cannon": CharacterClass(
            name="Glass Cannon",
            display_name="GLASS CANNON",
            title="The Explosive Marksman",
            max_hp=40,
            base_energy=8,
            starting_strength=5,
            starting_cards=[
                Card("Power Shot", "bolt dmg ~ 12.", 2, "Roll 1d12 damage", "attack", "uncommon"),
                Card("Mega Strike", "bolt dmg ~ 16.", 3, "Roll 1d16 damage", "attack", "rare"),
                Card("Quick Jab", "bolt dmg ~ 6.", 1, "Roll 1d6 damage", "attack", "common"),
                Card("Deflect", "bolt def ~ 4.", 1, "Roll 1d4 block", "defense", "common"),
            ],
            passive_ability="CRITICAL STRIKE",
            passive_description="25% chance to deal 1.5x damage on attacks.",
            color="#FF4444"
        ),

        "Necromancer": CharacterClass(
            name="Necromancer",
            display_name="NECROMANCER",
            title="The Dark Summoner",
            max_hp=65,
            base_energy=8,
            starting_strength=0,
            starting_cards=[
                Card("Shadow Bolt", "bolt dmg ~ 5.", 1, "Roll 1d5 damage", "attack", "common"),
                Card("Life Drain", "bolt dmg ~ 4. bolt heal ~ 3.", 2, "Roll 1d4 damage, heal 1d3", "attack_power", "uncommon"),
                Card("Bone Shield", "bolt def ~ 6.", 1, "Roll 1d6 block", "defense", "common"),
                Card("Dark Pact", "bolt pow ~ 2. bolt heal ~ 2.", 2, "Gain 2 strength, heal 1d2", "power", "uncommon"),
            ],
            passive_ability="SOUL HARVEST",
            passive_description="Heal 2 HP when an enemy dies.",
            color="#4A0080"
        ),

        "Chronomancer": CharacterClass(
            name="Chronomancer",
            display_name="CHRONOMANCER",
            title="The Time Bender",
            max_hp=70,
            base_energy=8,
            starting_strength=0,
            starting_cards=[
                Card("Time Strike", "bolt dmg ~ 6.", 1, "Roll 1d6 damage", "attack", "common"),
                Card("Chrono Shift", "bolt def ~ 8.", 2, "Roll 1d8 block", "defense", "common"),
                Card("Temporal Bolt", "bolt dmg ~ 7.", 2, "Roll 1d7 damage", "attack", "common"),
                Card("Time Warp", "bolt pow ~ 3.", 3, "Gain 3 strength", "power", "uncommon"),
            ],
            passive_ability="TIME WARP",
            passive_description="20% chance to get an extra turn after your turn ends.",
            color="#0080FF"
        ),
    }

    @classmethod
    def get_class(cls, name: str) -> Optional[CharacterClass]:
        """Get a class by name."""
        return cls.CLASSES.get(name)

    @classmethod
    def get_all_classes(cls) -> List[CharacterClass]:
        """Get all available classes."""
        return list(cls.CLASSES.values())

    @classmethod
    def get_class_names(cls) -> List[str]:
        """Get names of all classes."""
        return list(cls.CLASSES.keys())



# Tier of an enemy — affects HP range, attack pattern, and token reward.
class EnemyType(Enum):
    """Types of enemies."""
    MINION = "minion"
    NORMAL = "normal"
    ELITE = "elite"
    BOSS = "boss"

# A timed status effect on an enemy (vulnerable/weakened/poison/burn).
@dataclass
class EnemyDebuff:
    """
    Represents a debuff applied to an enemy.
    """
    name: str
    duration: int
    value: int = 0

    def __repr__(self):
        return f"EnemyDebuff({self.name}, {self.duration} turns)"

# Represents one enemy in a battle: HP, attack pattern, debuff list.
@dataclass
class Enemy:
    """
    Represents an enemy in battle.
    """
    name: str
    max_hp: int
    hp: int
    attack_pattern: str
    floor: int = 1
    enemy_type: EnemyType = EnemyType.NORMAL
    is_alive: bool = True
    buff_count: int = 0
    debuffs: List[EnemyDebuff] = field(default_factory=list)

    @classmethod
    def create_minion(cls, floor: int) -> 'Enemy':
        """Create a basic minion enemy."""
        names = ["Minor Glitch", "Stray Bug", "Loose Pointer", "Bug Swarm"]
        name = random.choice(names)
        base_hp = 10 + floor * 2
        return cls(
            name=name,
            max_hp=base_hp,
            hp=base_hp,
            attack_pattern="light",
            floor=floor,
            enemy_type=EnemyType.MINION
        )

    @classmethod
    def create_normal(cls, floor: int) -> 'Enemy':
        """Create a normal enemy."""
        names = ["The Compiler", "Memory Leak", "Stack Overflow", "Null Pointer"]
        name = random.choice(names)

        base_hp = random.randint(30, 40) + floor
        base_hp = min(base_hp, 50)
        return cls(
            name=name,
            max_hp=base_hp,
            hp=base_hp,
            attack_pattern="medium",
            floor=floor,
            enemy_type=EnemyType.NORMAL
        )

    @classmethod
    def create_elite(cls, floor: int) -> 'Enemy':
        """Create an elite enemy."""
        names = ["Stack Phantom", "Heap Horror", "Memory Beast", "The Garbage Collector"]
        name = random.choice(names)

        base_hp = random.randint(60, 70) + floor
        base_hp = min(base_hp, 80)
        return cls(
            name=name,
            max_hp=base_hp,
            hp=base_hp,
            attack_pattern="heavy",
            floor=floor,
            enemy_type=EnemyType.ELITE
        )

    @classmethod
    def create_boss(cls, floor: int) -> 'Enemy':
        """Create the final boss."""

        base_hp = random.randint(100, 110) + floor
        base_hp = min(base_hp, 120)
        return cls(
            name="The Heart of the Spire",
            max_hp=base_hp,
            hp=base_hp,
            attack_pattern="heavy",
            floor=floor,
            enemy_type=EnemyType.BOSS
        )

    def get_intent(self) -> Dict[str, Any]:
        """Get the enemy's next action intent."""
        patterns = {
            "light": {"damage": (5, 8), "type": "attack"},
            "medium": {"damage": (8, 12), "type": "attack"},
            "heavy": {"damage": (12, 18), "type": "attack"},
        }

        low, high = patterns.get(self.attack_pattern, (5, 8))["damage"]


        if self.enemy_type == EnemyType.BOSS:
            if random.random() < 0.3:
                return {"type": "special", "damage": 0, "description": "Charging..."}

        floor_bonus = max(0, self.floor - 1)
        damage = random.randint(low + floor_bonus, high + floor_bonus) + self.buff_count


        if self.get_debuff_multiplier() < 1.0:
            damage = int(damage * self.get_debuff_multiplier())

        return {
            "type": "attack",
            "damage": damage,
            "description": f"Attack for {low + floor_bonus}-{high + floor_bonus} damage"
        }

    def take_damage(self, amount: int):
        """Apply damage to the enemy, accounting for debuffs."""

        multiplier = self.get_debuff_multiplier()
        amount = int(amount * multiplier)


        poison_damage = self.get_debuff_damage()
        if poison_damage > 0:
            self.hp = max(0, self.hp - poison_damage)

        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False

    def heal(self, amount: int):
        """Heal the enemy."""
        self.hp = min(self.max_hp, self.hp + amount)

    def apply_buff(self, amount: int = 1):
        """Apply a buff to the enemy."""
        self.buff_count += amount

    def apply_debuff(self, debuff: EnemyDebuff):
        """Apply a debuff to the enemy."""

        for existing_debuff in self.debuffs:
            if existing_debuff.name == debuff.name:

                existing_debuff.duration = max(existing_debuff.duration, debuff.duration)
                existing_debuff.value = max(existing_debuff.value, debuff.value)
                return

        self.debuffs.append(debuff)

    def remove_debuff(self, debuff_name: str):
        """Remove a debuff from the enemy."""
        self.debuffs = [d for d in self.debuffs if d.name != debuff_name]

    def get_debuff_multiplier(self) -> float:
        """Get damage multiplier from debuffs."""
        multiplier = 1.0
        for debuff in self.debuffs:
            if debuff.name == "vulnerable":
                multiplier *= 1.5
            elif debuff.name == "weakened":
                multiplier *= 0.75
        return multiplier

    def get_debuff_damage(self) -> int:
        """Get damage from debuffs like poison/burn."""
        total = 0
        for debuff in self.debuffs:
            if debuff.name == "poison":
                total += debuff.value
            elif debuff.name == "burn":
                total += debuff.value
        return total

    def end_turn(self):
        """Called at end of enemy turn to reduce debuff durations."""
        for debuff in self.debuffs[:]:
            debuff.duration -= 1
            if debuff.duration <= 0:
                self.debuffs.remove(debuff)

    def __repr__(self):
        return f"Enemy({self.name}, HP: {self.hp}/{self.max_hp})"



# Every possible room type that can appear on the procedural dungeon map.
class NodeType(Enum):
    """Types of nodes on the map."""
    START = "start"
    ENEMY = "enemy"
    ELITE = "elite"
    SHOP = "shop"
    REST = "rest"
    TREASURE = "treasure"
    BOSS = "boss"
    EVENT = "event"

# One node on the dungeon map with its type, floor, position, and connections.
@dataclass
class MapNode:
    """
    Represents a node on the dungeon map.
    """
    node_id: int
    node_type: NodeType
    floor: int
    x: float
    y: float
    children: List[int] = field(default_factory=list)
    parents: List[int] = field(default_factory=list)
    visited: bool = False
    available: bool = False
    name: str = ""
    enemy: Optional[Enemy] = None

    def __repr__(self):
        return f"Node({self.node_id}, {self.node_type.value}, floor {self.floor})"

# Generates a 15-floor branching dungeon map as a DAG (directed acyclic graph).
# Each run is seeded differently so layout is never the same twice.
class ProceduralMap:
    """
    Generates a procedural dungeon map in the style of Slay the Spire.
    Creates a clean branching path through 15 floors using a DAG structure.

    Key algorithm:
    1. Create nodes for each floor
    2. Sort nodes by x-position
    3. Connect each node to proportional nodes on next floor (no overlaps)
    4. Every node has at least one parent from the previous floor
    """

    def __init__(self, num_floors: int = 15, seed: int = None):
        if seed is not None:
            random.seed(seed)

        self.num_floors = num_floors
        self.nodes: List[MapNode] = []
        self.current_node: Optional[MapNode] = None
        self.floor = 0
        self.completed = False


        self._floor_layouts = self._generate_floor_layouts()

        self._generate()

    def _generate_floor_layouts(self) -> Dict[int, Tuple[int, List[float]]]:
        """Generate randomized floor layouts. Each floor has 1-4 nodes at random x-positions."""
        layouts = {}

        for floor in range(self.num_floors + 1):

            if floor == 0 or floor % 5 == 0:
                layouts[floor] = (1, [0.5])
            else:

                num_nodes = random.randint(2, 4)



                positions = []
                spread = 0.4 + random.random() * 0.2
                start_x = 0.5 - spread / 2

                for i in range(num_nodes):

                    base_x = start_x + (spread / (num_nodes - 1)) * i if num_nodes > 1 else 0.5

                    offset = random.uniform(-0.05, 0.05)
                    pos = max(0.15, min(0.85, base_x + offset))
                    positions.append(pos)


                positions.sort()

                layouts[floor] = (num_nodes, positions)

        return layouts


    def _generate(self):
        """Generate the procedural map - Slay the Spire style."""
        self.nodes = []


        start = MapNode(
            node_id=0,
            node_type=NodeType.START,
            floor=0,
            x=0.5,
            y=0.0,
            name="Dungeon Entrance"
        )
        start.visited = True
        start.available = True
        self.nodes.append(start)
        self.current_node = start


        for floor in range(1, self.num_floors + 1):
            self._generate_floor(floor)


        last_floor_nodes = [n for n in self.nodes if n.floor == self.num_floors]
        for node in last_floor_nodes:
            node.node_type = NodeType.BOSS
            node.name = "The Heart of the Spire"


        for child_id in start.children:
            if child_id < len(self.nodes):
                self.nodes[child_id].available = True

    def _generate_floor(self, floor: int):
        """Generate a single floor with clean connections."""

        if floor in self._floor_layouts:
            num_nodes, x_positions = self._floor_layouts[floor]
        else:

            num_nodes = 3 if floor % 5 != 0 else 1
            x_positions = self._generate_x_positions(num_nodes)

        y_pos = floor / self.num_floors


        start_id = len(self.nodes)
        for i in range(num_nodes):
            x_pos = x_positions[i] if i < len(x_positions) else 0.5


            node_type = self._determine_node_type(floor, i, num_nodes)


            name = self._generate_node_name(node_type)

            node = MapNode(
                node_id=start_id + i,
                node_type=node_type,
                floor=floor,
                x=x_pos,
                y=y_pos,
                name=name
            )

            self.nodes.append(node)


        current_floor_nodes = [n for n in self.nodes if n.floor == floor]
        prev_floor_nodes = [n for n in self.nodes if n.floor == floor - 1]


        current_floor_nodes.sort(key=lambda n: n.x)
        prev_floor_nodes.sort(key=lambda n: n.x)


        self._connect_floors_proportional(prev_floor_nodes, current_floor_nodes)


        for node in current_floor_nodes:
            if self.current_node and self.current_node.node_id in node.parents:
                node.available = True

    def _generate_x_positions(self, num_nodes: int) -> List[float]:
        """Generate evenly spaced x-positions with slight randomness."""
        if num_nodes == 1:
            return [0.5]

        positions = []
        spread = 0.5
        start_x = 0.5 - spread / 2

        for i in range(num_nodes):

            base_x = start_x + (spread / (num_nodes - 1)) * i if num_nodes > 1 else 0.5
            offset = random.uniform(-0.05, 0.05)
            positions.append(max(0.2, min(0.8, base_x + offset)))

        return positions

    def _connect_floors_proportional(self, prev_nodes: List[MapNode], current_nodes: List[MapNode]):
        """
        Connect nodes between floors proportionally.
        This is the KEY to clean, non-overlapping map lines!

        Algorithm:
        - For each current node, find its proportional position
        - Connect it to the node at the same proportional position on prev floor
        - This ensures straight lines with no overlaps
        - EVERY node must have at least one child!
        """
        if not prev_nodes or not current_nodes:
            return


        prev_with_children = set()

        for curr in current_nodes:

            curr_proportion = (curr.x - 0.2) / 0.6 if len(current_nodes) > 1 else 0.5


            if len(prev_nodes) == 1:
                parent = prev_nodes[0]
            else:

                parent_idx = int(curr_proportion * (len(prev_nodes) - 1))
                parent_idx = max(0, min(len(prev_nodes) - 1, parent_idx))
                parent = prev_nodes[parent_idx]


            curr.parents.append(parent.node_id)
            parent.children.append(curr.node_id)
            prev_with_children.add(parent.node_id)


            if len(prev_nodes) > 1 and len(current_nodes) > 1:


                if curr_proportion < 0.33 and parent_idx > 0:

                    if random.random() < 0.4:
                        alt_parent = prev_nodes[parent_idx - 1]
                        if alt_parent.node_id not in curr.parents:
                            curr.parents.append(alt_parent.node_id)
                            alt_parent.children.append(curr.node_id)
                            prev_with_children.add(alt_parent.node_id)
                elif curr_proportion > 0.66 and parent_idx < len(prev_nodes) - 1:

                    if random.random() < 0.4:
                        alt_parent = prev_nodes[parent_idx + 1]
                        if alt_parent.node_id not in curr.parents:
                            curr.parents.append(alt_parent.node_id)
                            alt_parent.children.append(curr.node_id)
                            prev_with_children.add(alt_parent.node_id)



        for prev in prev_nodes:
            if prev.node_id not in prev_with_children:

                closest_curr = min(current_nodes, key=lambda c: abs(c.x - prev.x))
                closest_curr.parents.append(prev.node_id)
                prev.children.append(closest_curr.node_id)

    def _determine_node_type(self, floor: int, index: int, num_nodes: int) -> NodeType:
        """Determine what type of node this should be."""

        if floor == self.num_floors:
            return NodeType.BOSS


        if floor % 5 == 0:
            return NodeType.REST



        roll = random.random()


        elite_chance = 0.05 + (floor / self.num_floors) * 0.15
        shop_chance = 0.20
        treasure_chance = 0.15
        event_chance = 0.10

        if roll < elite_chance:

            if index == len(range(num_nodes)) // 2 or num_nodes <= 2:
                return NodeType.ELITE
            else:
                return NodeType.ENEMY
        elif roll < elite_chance + shop_chance:
            return NodeType.SHOP
        elif roll < elite_chance + shop_chance + treasure_chance:
            return NodeType.TREASURE
        elif roll < elite_chance + shop_chance + treasure_chance + event_chance:
            return NodeType.EVENT
        else:
            return NodeType.ENEMY

    def _generate_node_name(self, node_type: NodeType) -> str:
        """Generate a name for the node based on its type."""
        names = {
            NodeType.START: ["Dungeon Entrance", "The Beginning"],
            NodeType.ENEMY: [
                "Minor Glitch", "Stray Bug", "Loose Pointer", "Bug Swarm",
                "The Compiler", "Memory Leak", "Stack Overflow", "Null Pointer",
                "Syntax Error", "Runtime Panic", "Infinite Loop"
            ],
            NodeType.ELITE: [
                "Stack Phantom", "Heap Horror", "Memory Beast",
                "The Garbage Collector", "Buffer Overrun", "Race Condition"
            ],
            NodeType.SHOP: [
                "Binary Bazaar", "The Code Shop", "Item Vendor",
                "Merchant's Den", "Treasure Trader"
            ],
            NodeType.REST: [
                "Safe Haven", "Rest Point", "Camp Site",
                "Checkpoint", "Sanctuary"
            ],
            NodeType.TREASURE: [
                "Treasure Chest", "Loot Cache", "Hidden Vault",
                "Gold Pile", "Mystery Box"
            ],
            NodeType.EVENT: [
                "Strange Occurrence", "Mysterious Shrine", "Ancient Rune",
                "Code Anomaly", "Glitch in Reality"
            ],
            NodeType.BOSS: ["The Heart of the Spire", "Final Boss"],
        }

        return random.choice(names.get(node_type, ["Unknown"]))

    def get_current_node(self) -> Optional[MapNode]:
        """Get the currently selected node."""
        if not self.current_node and self.nodes:
            self.current_node = self.nodes[0]
        return self.current_node

    def get_available_nodes(self) -> List[MapNode]:
        """Get nodes available for selection."""
        return [n for n in self.nodes if n.available and not n.visited]

    def get_visited_nodes(self) -> List[MapNode]:
        """Get all visited nodes."""
        return [n for n in self.nodes if n.visited]

    def move_to(self, node_id: int) -> bool:
        """Move to a new node."""
        node = self.nodes[node_id]

        if not node.available or node.visited:
            return False


        if self.current_node:
            self.current_node.visited = True



        current_floor = node.floor
        for n in self.nodes:
            if n.floor == current_floor and n.node_id != node.node_id:
                n.visited = True
                n.available = False


        self.current_node = node
        self.current_node.visited = True
        self.current_node.available = False
        self.floor = node.floor


        for child_id in node.children:
            if child_id < len(self.nodes):
                self.nodes[child_id].available = True


        if node.node_type == NodeType.BOSS:
            self.completed = True

        return True

    def get_progress(self) -> Tuple[int, int]:
        """Get progress as (current_floor, total_floors)."""
        return (self.floor, self.num_floors)

    def reset(self, seed: int = None):
        """Reset the map with optional new seed."""
        if seed:
            random.seed(seed)
        self.__init__(self.num_floors)



# All player state: HP, energy, deck, hand, relics, tokens, stance.
@dataclass
class Player:
    """
    Represents the player character.
    """
    char_class: str
    max_hp: int
    hp: int
    max_energy: int
    energy: int
    strength: int
    block: int
    turn: int = 0
    draw_count: int = 5
    heal_at_combat_start: int = 0
    last_card_was_attack: bool = False
    attack_count: int = 0


    current_stance: Stance = field(default_factory=lambda: Stance.OBSERVATION)
    stance_locked_turns: int = 0


    deck: List[Card] = field(default_factory=list)
    hand: List[Card] = field(default_factory=list)
    discard_pile: List[Card] = field(default_factory=list)


    all_cards: List[Card] = field(default_factory=list)
    equipped_cards: List[Card] = field(default_factory=list)


    relics: List[Relic] = field(default_factory=list)
    equipped_relics: List[Relic] = field(default_factory=list)
    max_equipped_relics: int = 3
    max_relics: int = 10


    trace_elements: List[TraceElement] = field(default_factory=list)
    max_ingredients: int = 30


    tokens: int = 25


    is_alive: bool = True

    @classmethod
    def create(cls, class_name: str) -> 'Player':
        """Create a new player of the specified class."""
        profile = CharacterClassLibrary.get_class(class_name)
        if not profile:
            profile = CharacterClassLibrary.get_class("Ironclad")


        cards = [Card(c.name, c.code, c.energy_cost, c.description, c.card_type, c.rarity)
                 for c in profile.starting_cards]


        for card in CardLibrary.STARTER_CARDS:
            cards.append(Card(card.name, card.code, card.energy_cost, card.description,
                           card.card_type, card.rarity))

        return cls(
            char_class=class_name,
            max_hp=profile.max_hp,
            hp=profile.max_hp,
            max_energy=profile.base_energy,
            energy=profile.base_energy,
            strength=profile.starting_strength,
            block=0,
            deck=cards.copy(),
            all_cards=cards,
            equipped_cards=cards[:10]
        )

    def shuffle_deck(self):
        """Shuffle the deck."""
        random.shuffle(self.deck)

    def draw_cards(self, count: int = None):
        """Draw cards from deck to hand."""
        if count is None:
            count = self.draw_count

        for _ in range(count):
            self._draw_single_card()

    def _draw_single_card(self):
        """Draw a single card."""

        if not self.deck:
            if not self.discard_pile:
                return
            self.deck = self.discard_pile.copy()
            self.discard_pile = []
            self.shuffle_deck()


        if self.deck:
            card = self.deck.pop(0)
            self.hand.append(card)

    def play_card(self, card_index: int) -> Optional[Dict[str, Any]]:
        """Play a card from hand."""
        if card_index < 0 or card_index >= len(self.hand):
            return None

        card = self.hand[card_index]


        if card.energy_cost > self.energy:
            return None


        self.energy -= card.energy_cost


        result = card.execute()


        self._apply_card_effects(result, card)


        self.hand.pop(card_index)
        self.discard_pile.append(card)


        self.last_card_was_attack = card.card_type in ('attack', 'attack_power')
        if self.last_card_was_attack:
            self.attack_count += 1


        self._apply_class_effects(card)

        return result

    def _apply_card_effects(self, result: Dict[str, Any], card: Card):
        """Apply the results of a card."""

        damage = result.get('damage', 0)
        for relic in self.equipped_relics:
            damage += relic.get_bonus('damage')

        block = result.get('block', 0)
        for relic in self.equipped_relics:
            block += relic.get_bonus('block')


        damage = int(self.apply_stance_modifier(damage, is_outgoing=True))
        block = int(self.apply_stance_modifier(block, is_outgoing=True))


        if 'damage' in result and result['damage'] > 0:
            result['final_damage'] = damage + self.strength


        if block > 0:
            self.block += block


        heal = result.get('heal', 0)
        if heal > 0:
            self.heal(heal)


        strength_gain = result.get('strength', 0)
        if strength_gain > 0:
            self.strength += strength_gain

    def _apply_class_effects(self, card: Card):
        """Apply class-specific passive effects."""
        class_name = self.char_class



        if class_name == "Silent" and card.card_type in ('attack', 'attack_power'):
            self.gain_block(1)







    def gain_block(self, amount: int):
        """Gain block points."""

        modified_amount = int(self.apply_stance_modifier(amount, is_outgoing=True))
        self.block += modified_amount

    def take_damage(self, amount: int) -> int:
        """Take damage, applying block and stance modifiers first."""

        modified_amount = int(self.apply_stance_modifier(amount, is_outgoing=False))

        if self.block > 0:
            blocked = min(self.block, modified_amount)
            self.block -= blocked
            modified_amount -= blocked

        self.hp -= modified_amount
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False

        return amount

    def heal(self, amount: int):
        """Heal HP."""
        self.hp = min(self.max_hp, self.hp + amount)

    def reset_turn(self):
        """Reset for a new turn."""
        self.turn += 1
        self.energy = self.max_energy
        self.block = 0
        self.last_card_was_attack = False
        self.attack_count = 0


        if self.char_class == "Defect" and not self.last_card_was_attack:
            self.energy += 1

        if self.char_class == "Watcher" and self.turn % 2 == 1:
            self.strength += 1


        self.discard_pile.extend(self.hand)
        self.hand = []
        self.draw_cards()

    def add_card_to_deck(self, card: Card):
        """Add a card to the player's collection."""
        self.all_cards.append(card)
        if len(self.equipped_cards) < 10:
            self.equipped_cards.append(card)
            self.deck.append(card)

    def remove_card_from_deck(self, card_index: int) -> Optional[Card]:
        """Remove a card from the equipped deck."""
        if 0 <= card_index < len(self.equipped_cards):
            card = self.equipped_cards.pop(card_index)
            if card in self.deck:
                self.deck.remove(card)
            if card in self.hand:
                self.hand.remove(card)
            return card
        return None

    def add_relic(self, relic: Relic):
        """Add a relic to inventory. Equip automatically if a slot is free."""
        if relic in self.relics:
            return False
        self.relics.append(relic)

        if len(self.equipped_relics) < self.max_equipped_relics:
            self.equip_relic(relic)
        return True

    def equip_relic(self, relic: Relic) -> bool:
        """Equip a relic if slot is available."""
        if relic not in self.relics or relic in self.equipped_relics:
            return False
        if len(self.equipped_relics) >= self.max_equipped_relics:
            return False
        self.equipped_relics.append(relic)
        relic.apply(self)
        return True

    def unequip_relic(self, relic: Relic) -> bool:
        """Unequip a relic and keep it in inventory."""
        if relic not in self.equipped_relics:
            return False
        self.equipped_relics.remove(relic)
        relic.remove(self)
        return True

    def remove_relic(self, relic: Relic) -> bool:
        """Remove a relic from inventory and revert its effects."""
        if relic in self.equipped_relics:
            self.unequip_relic(relic)
        if relic in self.relics:
            self.relics.remove(relic)
            return True
        return False

    def add_ingredient(self, element: TraceElement) -> bool:
        """Add a trace element to inventory for crafting."""
        if len(self.trace_elements) < self.max_ingredients:
            self.trace_elements.append(element)
            return True
        return False

    def craft_card(self, card_index: int, element_index: int) -> Optional[Card]:
        """Craft a card with a trace element.

        Args:
            card_index: Index in equipped_cards
            element_index: Index in trace_elements

        Returns:
            The crafted card, or None if crafting fails
        """
        if not (0 <= card_index < len(self.equipped_cards)):
            return None
        if not (0 <= element_index < len(self.trace_elements)):
            return None

        card = self.equipped_cards[card_index]
        element = self.trace_elements[element_index]


        crafted = CraftingRecipeLibrary.craft(card, element)

        if crafted:

            self.equipped_cards[card_index] = crafted
            if card in self.deck:
                idx = self.deck.index(card)
                self.deck[idx] = crafted


            self.trace_elements.pop(element_index)

            return crafted

        return None

    def get_craftable_recipes(self) -> List[Tuple[Card, TraceElement, CraftingRecipe]]:
        """Get all possible crafting combinations available."""
        recipes = []

        for card in self.equipped_cards:
            for element in self.trace_elements:
                recipe = CraftingRecipeLibrary.find_recipe(card, element)
                if recipe:
                    recipes.append((card, element, recipe))

        return recipes

    def heal_at_battle_start(self):
        """Heal at the start of battle."""
        if self.heal_at_combat_start > 0:
            self.heal(self.heal_at_combat_start)

    def toggle_stance(self) -> bool:
        """Toggle between OBSERVATION and INTERVENTION stances.

        Returns True if stance was toggled, False if locked.
        """
        if self.stance_locked_turns > 0:
            return False

        if self.current_stance == Stance.OBSERVATION:
            self.current_stance = Stance.INTERVENTION
        else:
            self.current_stance = Stance.OBSERVATION

        return True

    def apply_stance_modifier(self, value: float, is_outgoing: bool) -> float:
        """Apply stance modifier to a card effect value.

        Args:
            value: The base value (damage, block, heal)
            is_outgoing: True for damage/effects we deal, False for damage we take

        Returns:
            Modified value based on current stance
        """
        if self.current_stance == Stance.OBSERVATION:

            if is_outgoing:
                return value * 0.7
            else:
                return value * 0.7
        else:

            if is_outgoing:
                return value * 1.3
            else:
                return value * 1.3

    def get_status(self) -> str:
        """Get a status string for the player."""
        return (f"HP: {self.hp}/{self.max_hp} | "
                f"Energy: {self.energy}/{self.max_energy} | "
                f"Block: {self.block} | "
                f"Strength: {self.strength}")

    def __repr__(self):
        return f"Player({self.char_class}, HP: {self.hp}/{self.max_hp})"



# Manages one combat encounter: tracks turns, logs, and win/lose state.
@dataclass
class Battle:
    """
    Represents a battle between player and enemy.
    """
    player: Player
    enemy: Enemy
    turn: int = 1
    log: List[str] = field(default_factory=list)
    is_over: bool = False
    player_won: bool = False

    def __post_init__(self):

        self.player.heal_at_battle_start()


        self.player.draw_cards()

    def player_action(self, card_index: int) -> Dict[str, Any]:
        """Player plays a card."""
        result = self.player.play_card(card_index)

        if result is None:
            self.log.append("Cannot play that card!")
            return {"success": False, "log": "Not enough energy or invalid card"}



        damage = result.get('final_damage', 0)


        if damage == 0 and 'damage' in result:
            damage = result.get('damage', 0)

        if damage > 0:

            if self.player.char_class == "Glass Cannon" and random.random() < 0.25:
                damage = int(damage * 1.5)
                self.log.append(f"CRITICAL HIT! Damage increased to {damage}!")


        self.enemy.take_damage(damage)
        if damage > 0:
            self.log.append(f"Dealt {damage} damage to {self.enemy.name}!")


        if not self.enemy.is_alive:
            self._on_victory()
            return {
                "success": True,
                "damage": damage,
                "block": 0,
                "heal": 0,
                "strength": 0,
                "rolls": result.get("rolls", []),
                "enemy_hp": self.enemy.hp,
                "log": "\n".join(self.log[-5:])
            }


        block = result.get('block', 0)
        if block > 0:
            self.log.append(f"Gained {block} block!")

        heal = result.get('heal', 0)
        if heal > 0:
            self.log.append(f"Healed for {heal} HP!")

        strength = result.get('strength', 0)
        if strength > 0:
            self.log.append(f"Gained {strength} strength!")

        return {
            "success": True,
            "damage": damage,
            "block": block,
            "heal": heal,
            "strength": strength,
            "rolls": result.get("rolls", []),
            "enemy_hp": self.enemy.hp,
            "log": "\n".join(self.log[-5:])
        }

    def enemy_action(self) -> Dict[str, Any]:
        """Enemy takes their turn."""
        intent = self.enemy.get_intent()
        actual_damage = 0

        if intent["type"] == "attack":
            damage = intent["damage"]
            actual_damage = self.player.take_damage(damage)
            self.log.append(f"{self.enemy.name} attacks for {actual_damage} damage!")
        elif intent["type"] == "special":
            self.log.append(f"{self.enemy.name} is charging a powerful attack!")
            self.enemy.apply_buff(3)


        if not self.player.is_alive:
            self._on_defeat()

        return {
            "damage_taken": actual_damage,
            "intent": intent,
            "player_hp": self.player.hp,
            "log": "\n".join(self.log[-3:])
        }

    def end_player_turn(self) -> Dict[str, Any]:
        """End the player's turn."""

        if self.player.char_class == "Ironclad":
            self.player.heal(1)
            self.log.append("Ironclad heals 1 HP.")


        if self.player.char_class == "Chronomancer" and random.random() < 0.2:
            self.log.append("TIME WARP! You get an extra turn!")

            self.player.discard_pile.extend(self.player.hand)
            self.player.hand = []
            self.turn += 1
            self.player.reset_turn()
            return {
                "extra_turn": True,
                "turn": self.turn,
                "player_hp": self.player.hp,
                "damage_taken": 0,
                "intent": {"type": "none", "damage": 0, "description": "Time Warped!"},
                "log": "\n".join(self.log[-3:])
            }


        self.player.discard_pile.extend(self.player.hand)
        self.player.hand = []


        enemy_result = self.enemy_action()


        if self.is_over:
            return enemy_result


        self.turn += 1
        self.player.reset_turn()

        return {
            "extra_turn": False,
            "turn": self.turn,
            **enemy_result
        }

    def _on_victory(self):
        """Handle player victory."""
        self.is_over = True
        self.player_won = True
        self.log.append(f"Victory! {self.enemy.name} defeated!")


        if getattr(self.enemy, 'enemy_type', None) in (EnemyType.ELITE, EnemyType.BOSS):
            if len(self.player.relics) < getattr(self.player, 'max_relics', 3):
                relic = RelicLibrary.get_random_relic(floor=self.enemy.floor)
                self.player.add_relic(relic)
                self.log.append(f"Looted a Relic: {relic.name}!")
            else:
                self.log.append("Looted a Relic, but inventory is full!")


        if self.player.char_class == "Necromancer":
            self.player.heal(2)
            self.log.append("Soul Harvest: Healed 2 HP!")

    def _on_defeat(self):
        """Handle player defeat."""
        self.is_over = True
        self.player_won = False
        self.log.append("Defeat! You have fallen...")

    def get_log(self) -> str:
        """Get the full battle log."""
        return "\n".join(self.log)

    def get_state(self) -> Dict[str, Any]:
        """Get current battle state."""
        return {
            "turn": self.turn,
            "player_hp": self.player.hp,
            "player_max_hp": self.player.max_hp,
            "player_energy": self.player.energy,
            "player_max_energy": self.player.max_energy,
            "player_block": self.player.block,
            "player_strength": self.player.strength,
            "enemy_hp": self.enemy.hp,
            "enemy_max_hp": self.enemy.max_hp,
            "enemy_intent": self.enemy.get_intent(),
            "hand_size": len(self.player.hand),
            "is_over": self.is_over,
            "player_won": self.player_won if self.is_over else None,
            "log": self.log[-10:]
        }



# All possible top-level screens/states the game can be in.
class GameState(Enum):
    """Possible game states."""
    MAIN_MENU = "main_menu"
    CLASS_SELECT = "class_select"
    MAP = "map"
    BATTLE = "battle"
    SHOP = "shop"
    REST = "rest"
    REWARD = "reward"
    VICTORY = "victory"
    DEFEAT = "defeat"
    INVENTORY = "inventory"

# Central game controller: owns the map, player, and current battle.
# Routes between map traversal, combat, shop, and rewards.
class Game:
    """
    Main game class that manages the game state and flow.
    """

    def __init__(self, class_name: str = None):
        self.state = GameState.MAIN_MENU
        self.player: Optional[Player] = None
        self.battle: Optional[Battle] = None
        self.game_map: Optional[ProceduralMap] = None
        self.current_enemy: Optional[Enemy] = None
        self.floor = 0
        self.total_floors = 15

        if class_name:
            self.start_game(class_name)

    def start_game(self, class_name: str):
        """Start a new game with the specified class."""
        self.player = Player.create(class_name)

        import time
        self.game_map = ProceduralMap(self.total_floors, seed=int(time.time() * 1000) % 1000000)

        if self.game_map and self.game_map.nodes:
            self.game_map.current_node = self.game_map.nodes[0]
        self.floor = self.game_map.current_node.floor if self.game_map.current_node else 0
        self.state = GameState.MAP
        self.floor = 0

    def get_current_node(self) -> Optional[MapNode]:
        """Get the current map node."""
        if self.game_map:
            return self.game_map.get_current_node()
        return None

    def get_available_nodes(self) -> List[MapNode]:
        """Get available map nodes."""
        if self.game_map:
            return self.game_map.get_available_nodes()
        return []

    def enter_node(self, node_id: int) -> Tuple[GameState, str]:
        """Enter a map node and handle its event. Returns (new_state, message)."""
        if not self.game_map:
            return self.state, ""

        node = self.game_map.nodes[node_id]
        self.game_map.move_to(node_id)
        self.floor = node.floor
        message = ""

        if node.node_type in (NodeType.ENEMY, NodeType.ELITE, NodeType.BOSS):

            self._prepare_for_battle()

            if node.node_type == NodeType.ENEMY:
                self.current_enemy = Enemy.create_normal(self.floor)
            elif node.node_type == NodeType.ELITE:
                self.current_enemy = Enemy.create_elite(self.floor)
            else:
                self.current_enemy = Enemy.create_boss(self.floor)

            self.battle = Battle(self.player, self.current_enemy)
            self.state = GameState.BATTLE
            message = f"Battle against {self.current_enemy.name}!"

        elif node.node_type == NodeType.SHOP:
            self.state = GameState.SHOP
            message = "Welcome to the Binary Bazaar!"

        elif node.node_type == NodeType.REST:
            message = self._do_rest()
            self.state = GameState.MAP

        elif node.node_type == NodeType.TREASURE:
            message = self._do_treasure()
            self.state = GameState.MAP

        elif node.node_type == NodeType.EVENT:
            message = self._do_event()
            self.state = GameState.MAP

        self.last_event_message = message
        return self.state, message

    def _prepare_for_battle(self):
        """Prepare the player's deck for a new battle."""

        self.player.deck = [Card(c.name, c.code, c.energy_cost, c.description, c.card_type, c.rarity)
                           for c in self.player.equipped_cards]
        self.player.hand = []
        self.player.discard_pile = []
        self.player.block = 0
        self.player.turn = 0
        self.player.energy = self.player.max_energy
        self.player.shuffle_deck()

    def _do_rest(self) -> str:
        """Handle rest node. Returns description."""
        heal_amount = int(self.player.max_hp * 0.3)
        self.player.heal(heal_amount)
        return f"🏕️ REST SITE\n\nYou rest by the campfire.\n\nHealed {heal_amount} HP!\n\nHP: {self.player.hp}/{self.player.max_hp}"

    def _do_treasure(self) -> str:
        """Handle treasure node. Returns description."""
        tokens_found = random.randint(60, 100) + self.floor * 8
        self.player.tokens += tokens_found
        messages = [f"💎 TREASURE FOUND!\n\nYou found a treasure chest!\n+{tokens_found} tokens"]


        if len(self.player.relics) < getattr(self.player, 'max_relics', 3):
            relic = RelicLibrary.get_random_relic(floor=self.floor)
            self.player.add_relic(relic)
            messages.append(f"Found relic: {relic.name}!")
        else:
            messages.append("You found a relic, but your inventory is full!")


        if random.random() < 0.5:
            card = CardLibrary.get_random_card(self.floor)
            self.player.add_card_to_deck(card)
            messages.append(f"Found card: {card.name} ({card.energy_cost}E) - {card.code}")


        if random.random() < 0.3:
            element = TraceElementLibrary.get_random_element(floor=self.floor)
            self.player.add_ingredient(element)
            messages.append(f"Found trace element: {element.name} — {element.description}")

        return "\n".join(messages)

    def _do_event(self) -> str:
        """Handle random event. Returns description."""
        roll = random.random()

        # Each event has a probability range, an action lambda, and a message.
        events = [
            {
                "range": (0.0, 0.15),
                "title": "❓ MYSTERIOUS SHRINE",
                "action": lambda: setattr(self.player, 'tokens', self.player.tokens + 75),
                "message": "A glowing shrine blesses you with riches.\n+75 tokens!"
            },
            {
                "range": (0.15, 0.30),
                "title": "❓ ANCIENT TRAINING GROUND",
                "action": lambda: setattr(self.player, 'strength', self.player.strength + 2),
                "message": "You find an ancient training ground and hone your skills.\n+2 Strength!"
            },
            {
                "range": (0.30, 0.45),
                "title": "❓ WANDERING MERCHANT",
                "action": lambda: self.player.add_card_to_deck(CardLibrary.get_random_card(self.floor)),
                "message": f"A wandering merchant offers you a free card!"
            },
            {
                "range": (0.45, 0.60),
                "title": "❓ HEALING SPRING",
                "action": lambda: self.player.heal(15),
                "message": "You discover a healing spring.\n+15 HP!"
            },
            {
                "range": (0.60, 0.70),
                "title": "❓ TRAP!",
                "action": lambda: self.player.take_damage(8),
                "message": "You triggered a hidden trap!\n-8 HP!"
            },
            {
                "range": (0.70, 0.80),
                "title": "❓ CURSED GROUND",
                "action": lambda: self.player.take_damage(5),
                "message": "The ground saps your life force.\n-5 HP!"
            },
            {
                "range": (0.80, 0.90),
                "title": "❓ RELIC DISCOVERY",
                "action": lambda: self.player.add_relic(RelicLibrary.get_random_relic()) if len(self.player.relics) < self.player.max_relics else None,
                "message": "You discover an ancient relic!" if len(self.player.relics) < self.player.max_relics else "You find a relic but your inventory is full!"
            },
            {
                "range": (0.90, 1.0),
                "title": "❓ TRACE ELEMENT CACHE",
                "action": lambda: self.player.add_ingredient(TraceElementLibrary.get_random_element("rare", self.floor)),
                "message": "You uncover a cache of rare crafting materials!"
            },
        ]

        for event in events:
            low, high = event["range"]
            if low <= roll < high:
                event["action"]()
                return f"{event['title']}\n\n{event['message']}\n\nHP: {self.player.hp}/{self.player.max_hp}"

        self.player.tokens += 30
        return "❓ STRANGE OCCURRENCE\n\nSomething odd happened.\n+30 tokens"

    def end_battle(self, won: bool):
        """Handle end of battle."""
        if won:
            # Boss kill → go straight to victory, no token drop needed
            if self.current_enemy and self.current_enemy.enemy_type == EnemyType.BOSS:
                self.state = GameState.VICTORY
                self.battle = None
                return

            # Token reward scales with enemy tier and floor depth.
            # Minion: 15-30 | Normal: 40-60 | Elite: 80-120, all +5 per floor.
            floor_bonus = self.floor * 5
            if self.current_enemy and self.current_enemy.enemy_type == EnemyType.ELITE:
                reward = random.randint(80, 120) + floor_bonus
            elif self.current_enemy and self.current_enemy.enemy_type == EnemyType.MINION:
                reward = random.randint(15, 30) + floor_bonus
            else:
                reward = random.randint(40, 60) + floor_bonus

            self.player.tokens += reward

            # Always drop a crafting ingredient after combat
            element = TraceElementLibrary.get_random_element(floor=self.floor)
            self.player.add_ingredient(element)
            self.state = GameState.MAP
        else:
            self.state = GameState.DEFEAT

        self.battle = None
        self.current_enemy = None

    def buy_card(self, card: Card) -> bool:
        """Deduct tokens and add card to the player's collection."""
        # Cost: base 30 + 15 per energy point, capped at 250.
        cost = min(250, 30 + card.energy_cost * 15)
        if self.player.tokens < cost:
            return False
        self.player.tokens -= cost
        self.player.add_card_to_deck(card)
        return True

    def get_card_cost(self, card: Card) -> int:
        """Return the shop price of a card."""
        return min(250, 30 + card.energy_cost * 15)

    def buy_relic(self, relic: Relic) -> bool:
        """Deduct tokens and add relic to player inventory (rarity-based price)."""
        cost = self.get_relic_cost(relic)
        if self.player.tokens < cost:
            return False
        if len(self.player.relics) >= self.player.max_relics:
            return False
        self.player.tokens -= cost
        self.player.add_relic(relic)
        return True

    def get_relic_cost(self, relic: Relic) -> int:
        """Relic shop price scales with rarity: common 40, uncommon 80, rare 150, legendary 300."""
        return {'common': 40, 'uncommon': 80, 'rare': 150, 'legendary': 300}.get(relic.rarity, 80)

    def remove_card(self, card_index: int) -> Optional[Card]:
        """Remove a card from deck."""
        return self.player.remove_card_from_deck(card_index)

    def is_game_over(self) -> bool:
        """Check if game is over."""
        return self.state in (GameState.VICTORY, GameState.DEFEAT)

    def is_victory(self) -> bool:
        """Check if player won."""
        return self.state == GameState.VICTORY



# Top-level Tkinter GUI: builds every screen and routes user input to Game.
class CodeSpireGUI:
    """
    Main GUI class for Code Spire.
    Handles all user interface and game display.
    """


    COLORS = {
        'background': '#2b1b17',
        'panel_bg': '#3e2723',
        'header_bg': '#1b120f',
        'text_primary': '#e8dcc7',
        'text_secondary': '#b0a080',
        'gold': '#d4af37',
        'red': '#b33030',
        'green': '#2e5c31',
        'blue': '#3b5f8f',
        'purple': '#6b3e75',
        'orange': '#c87a27',
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{GAME_NAME} - {SUBTITLE}")
        self.root.geometry("1200x800")
        self.root.configure(bg=self.COLORS['background'])
        self.root.resizable(True, True)


        self.game: Optional[Game] = None
        self.selected_card_index: Optional[int] = None
        self.shop_cards: List[Card] = []
        self.shop_relics: List[Relic] = []
        self.reward_cards: List[Card] = []


        self.frames: Dict[str, tk.Frame] = {}


        sprite_manager.initialize()


        self._build_all_frames()


        self._show_frame('main_menu')

    def _build_all_frames(self):
        """Build all UI frames/screens."""
        self._build_main_menu()
        self._build_class_select()
        self._build_map_screen()
        self._build_battle_screen()
        self._build_reward_screen()
        self._build_shop_screen()
        self._build_inventory_screen()
        self._build_end_screen()
        self._build_help_screen()

    def _create_frame(self, name: str) -> tk.Frame:
        """Create a new frame."""
        frame = tk.Frame(self.root, bg=self.COLORS['background'])
        self.frames[name] = frame
        return frame

    def _show_frame(self, name: str):
        """Show a specific frame and hide others."""
        for frame in self.frames.values():
            frame.pack_forget()

        if name in self.frames:
            self.frames[name].pack(fill=tk.BOTH, expand=True)



    def _build_main_menu(self):
        """Build the main menu screen."""
        frame = self._create_frame('main_menu')


        title_frame = tk.Frame(frame, bg=self.COLORS['header_bg'])
        title_frame.pack(fill=tk.X, pady=20)

        tk.Label(
            title_frame,
            text=f"⚔️ {GAME_NAME} ⚔️",
            font=("Times New Roman", 48, "bold"),
            fg=self.COLORS['gold'],
            bg=self.COLORS['header_bg']
        ).pack(pady=20)

        tk.Label(
            title_frame,
            text=SUBTITLE,
            font=("Times New Roman", 18, "italic"),
            fg=self.COLORS['text_secondary'],
            bg=self.COLORS['header_bg']
        ).pack(pady=(0, 20))


        btn_frame = tk.Frame(frame, bg=self.COLORS['background'])
        btn_frame.pack(pady=50)

        buttons = [
            ("⚔️ ENTER THE DUNGEON ⚔️", self._show_class_select, self.COLORS['red']),
            ("📜 READ HEROSCRIPT 📜", self._show_help, self.COLORS['blue']),
            ("🚪 EXIT 🚪", self.root.quit, '#8B4513'),
        ]

        for text, command, color in buttons:
            tk.Button(
                btn_frame,
                text=text,
                font=("Times New Roman", 20, "bold"),
                bg=color,
                fg=self.COLORS['text_primary'],
                width=30,
                height=2,
                bd=4,
                relief=tk.RAISED,
                cursor="hand2",
                command=command
            ).pack(pady=15)


        tk.Label(
            frame,
            text=f"Version {VERSION}",
            font=("Courier New", 10),
            fg=self.COLORS['text_secondary'],
            bg=self.COLORS['background']
        ).pack(side=tk.BOTTOM, pady=10)



    def _build_class_select(self):
        """Build the class selection screen."""
        frame = self._create_frame('class_select')


        header = tk.Frame(frame, bg=self.COLORS['header_bg'])
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="⚔️ CHOOSE YOUR HERO ⚔️",
            font=("Times New Roman", 32, "bold"),
            fg=self.COLORS['gold'],
            bg=self.COLORS['header_bg']
        ).pack(pady=20)

        tk.Button(
            header,
            text="← Back to Menu",
            font=("Times New Roman", 12),
            bg='#4a3020',
            fg=self.COLORS['gold'],
            command=lambda: self._show_frame('main_menu')
        ).pack(pady=10)


        canvas_frame = tk.Frame(frame, bg=self.COLORS['background'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        canvas = tk.Canvas(canvas_frame, bg=self.COLORS['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['background'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


        classes = CharacterClassLibrary.get_all_classes()

        for cls in classes:
            self._build_class_card(scrollable_frame, cls)

    def _build_class_card(self, parent: tk.Frame, cls: CharacterClass):
        """Build a single class selection card."""
        card = tk.Frame(parent, bg=self.COLORS['panel_bg'], bd=4, relief=tk.RAISED)
        card.pack(fill=tk.X, padx=20, pady=15)


        header = tk.Frame(card, bg=cls.color)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text=cls.display_name,
            font=("Times New Roman", 20, "bold"),
            fg=self.COLORS['gold'],
            bg=cls.color,
            width=20
        ).pack(pady=(10, 2))

        tk.Label(
            header,
            text=cls.title,
            font=("Times New Roman", 12, "italic"),
            fg=self.COLORS['text_secondary'],
            bg=cls.color
        ).pack(pady=(0, 10))


        info = tk.Frame(card, bg=self.COLORS['panel_bg'])
        info.pack(fill=tk.X, padx=20, pady=10)

        stats = f"HP: {cls.max_hp} | Energy: {cls.base_energy} | Strength: {cls.starting_strength}"
        tk.Label(
            info,
            text=stats,
            font=("Courier New", 11),
            fg=self.COLORS['text_primary'],
            bg=self.COLORS['panel_bg']
        ).pack()

        tk.Label(
            info,
            text=f"Passive: {cls.passive_ability}",
            font=("Courier New", 10, "bold"),
            fg=self.COLORS['purple'],
            bg=self.COLORS['panel_bg']
        ).pack(pady=(5, 0))

        tk.Label(
            info,
            text=cls.passive_description,
            font=("Courier New", 9),
            fg=self.COLORS['text_secondary'],
            bg=self.COLORS['panel_bg'],
            wraplength=600
        ).pack()


        cards_label = tk.Label(
            info,
            text="Starting Cards:",
            font=("Courier New", 10, "bold"),
            fg=self.COLORS['blue'],
            bg=self.COLORS['panel_bg']
        )
        cards_label.pack(pady=(10, 5))

        for card_obj in cls.starting_cards:
            tk.Label(
                info,
                text=f"  • {card_obj.name} ({card_obj.energy_cost}E): {card_obj.description}",
                font=("Courier New", 9),
                fg=self.COLORS['text_secondary'],
                bg=self.COLORS['panel_bg'],
                anchor=tk.W
            ).pack(anchor=tk.W)


        tk.Button(
            card,
            text=f"⚔️ SELECT {cls.display_name} ⚔️",
            font=("Times New Roman", 14, "bold"),
            bg=cls.color,
            fg=self.COLORS['text_primary'],
            width=30,
            cursor="hand2",
            command=lambda c=cls.name: self._start_game(c)
        ).pack(pady=15)

    def _show_class_select(self):
        """Show the class selection screen."""
        self._show_frame('class_select')

    def _start_game(self, class_name: str):
        """Start a new game with the selected class."""
        self.game = Game(class_name)
        self._show_map()



    def _build_map_screen(self):
        """Build the dungeon map screen."""
        frame = self._create_frame('map')


        top_bar = tk.Frame(frame, bg=self.COLORS['header_bg'])
        top_bar.pack(fill=tk.X)

        self.map_floor_label = tk.Label(
            top_bar,
            text="Floor 0/15",
            font=("Courier New", 14, "bold"),
            fg=self.COLORS['gold'],
            bg=self.COLORS['header_bg']
        )
        self.map_floor_label.pack(side=tk.LEFT, padx=20, pady=10)

        self.map_player_stats = tk.Label(
            top_bar,
            text="",
            font=("Courier New", 11),
            fg=self.COLORS['text_primary'],
            bg=self.COLORS['header_bg']
        )
        self.map_player_stats.pack(side=tk.RIGHT, padx=20, pady=10)


        tk.Label(
            frame,
            text="🗺️ DUNGEON MAP 🗺️",
            font=("Times New Roman", 24, "bold"),
            fg=self.COLORS['gold'],
            bg=self.COLORS['background']
        ).pack(pady=15)


        legend_frame = tk.Frame(frame, bg=self.COLORS['panel_bg'])
        legend_frame.pack(fill=tk.X, padx=20)

        legend_items = [
            ("⚔️", "Enemy", '#8B0000'),
            ("💀", "Elite", '#8B4513'),
            ("🏪", "Shop", '#DAA520'),
            ("🏕️", "Rest", '#228B22'),
            ("💎", "Treasure", '#FFD700'),
            ("👹", "Boss", '#4B0082'),
            ("❓", "Event", '#808080'),
        ]

        for icon, name, color in legend_items:
            tk.Label(
                legend_frame,
                text=f"{icon} {name}",
                font=("Courier New", 10),
                fg=color,
                bg=self.COLORS['panel_bg']
            ).pack(side=tk.LEFT, padx=10, pady=5)


        map_container = tk.Frame(frame, bg=self.COLORS['background'])
        map_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.map_canvas = tk.Canvas(
            map_container,
            bg=self.COLORS['background'],
            highlightthickness=0,
            cursor="hand2",
        )
        map_scrollbar = tk.Scrollbar(map_container, orient=tk.VERTICAL, command=self.map_canvas.yview)
        self.map_canvas.configure(yscrollcommand=map_scrollbar.set)

        self.map_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        map_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.map_canvas.bind("<Button-1>", self._on_map_canvas_click)

        self.map_canvas.bind("<MouseWheel>", lambda e: self.map_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        self.node_click_map = {}


        bottom = tk.Frame(frame, bg=self.COLORS['background'])
        bottom.pack(fill=tk.X, pady=10)

        tk.Button(
            bottom,
            text="📦 Inventory",
            font=("Times New Roman", 12),
            bg='#4a3060',
            fg=self.COLORS['text_primary'],
            command=self._show_inventory
        ).pack(side=tk.LEFT, padx=20)

        tk.Button(
            bottom,
            text="← Main Menu",
            font=("Times New Roman", 12),
            bg='#4a3020',
            fg=self.COLORS['gold'],
            command=lambda: self._show_frame('main_menu')
        ).pack(side=tk.RIGHT, padx=20)

    def _show_map(self):
        """Update and show the map screen with visual tree."""
        if not self.game:
            return


        if not self.game.game_map or not self.game.game_map.nodes:
            self.game.game_map = ProceduralMap(self.game.total_floors)
            if self.game.game_map.nodes:
                self.game.game_map.current_node = self.game.game_map.nodes[0]

        if not self.game.game_map:
            return

        if not self.game.game_map.current_node and self.game.game_map.nodes:
            self.game.game_map.current_node = self.game.game_map.nodes[0]

        self._show_frame('map')


        self.root.update_idletasks()


        floor = self.game.game_map.floor
        self.map_floor_label.config(text=f"Floor {floor}/{self.game.total_floors}")


        if self.game.player:
            stats = (f"HP: {self.game.player.hp}/{self.game.player.max_hp} | "
                    f"Tokens: {self.game.player.tokens} | "
                    f"Relics: {len(self.game.player.relics)}/{self.game.player.max_relics}")
            self.map_player_stats.config(text=stats)


        self._draw_map_tree()

    def _calculate_node_position(self, node: 'MapNode', canvas_width: int, map_height: int) -> Tuple[int, int]:
        """Calculate the exact pixel position of a node on the canvas."""
        x = int(node.x * canvas_width)
        y = int((node.floor / (self.game.game_map.num_floors + 1)) * (map_height - 40) + 20)
        return x, y

    def _draw_map_tree(self):
        """Draw the procedural map as a visual tree."""
        if not self.game or not self.game.game_map:
            return

        self.map_canvas.delete("all")
        self.node_click_map = {}

        game_map = self.game.game_map


        current = game_map.get_current_node()
        if current:

            for child_id in current.children:
                if child_id < len(game_map.nodes):
                    game_map.nodes[child_id].available = True



        canvas_width = max(800, self.map_canvas.winfo_width())
        canvas_height = max(600, self.map_canvas.winfo_height())


        map_height = (game_map.num_floors + 2) * 80
        self.map_canvas.configure(scrollregion=(0, 0, canvas_width, map_height))


        for node in game_map.nodes:
            for child_id in node.children:
                if child_id < len(game_map.nodes):
                    child = game_map.nodes[child_id]


                    x1, y1 = self._calculate_node_position(node, canvas_width, map_height)
                    x2, y2 = self._calculate_node_position(child, canvas_width, map_height)


                    line_color = '#444444'
                    if child.available:
                        line_color = '#888800'
                    if node.visited and child.visited:
                        line_color = '#005500'

                    self.map_canvas.create_line(
                        x1, y1, x2, y2,
                        fill=line_color,
                        width=2
                    )


        for node in game_map.nodes:
            self._draw_map_node(node, canvas_width, map_height)


        if current:
            _, target_y = self._calculate_node_position(current, canvas_width, map_height)
            scroll_fraction = (target_y - canvas_height / 2) / map_height
            self.map_canvas.yview_moveto(max(0.0, min(1.0, scroll_fraction)))

    def _draw_map_node(self, node: MapNode, canvas_width: int, map_height: int):
        """Draw a single node on the map canvas."""
        if not self.game or not self.game.game_map:
            return


        x, y = self._calculate_node_position(node, canvas_width, map_height)


        colors = {
            NodeType.ENEMY: '#8B0000',
            NodeType.ELITE: '#8B4513',
            NodeType.SHOP: '#DAA520',
            NodeType.REST: '#228B22',
            NodeType.TREASURE: '#FFD700',
            NodeType.BOSS: '#4B0082',
            NodeType.EVENT: '#808080',
            NodeType.START: '#505050',
        }

        icons = {
            NodeType.ENEMY: "⚔️",
            NodeType.ELITE: "💀",
            NodeType.SHOP: "🏪",
            NodeType.REST: "🏕️",
            NodeType.TREASURE: "💎",
            NodeType.BOSS: "👹",
            NodeType.EVENT: "❓",
            NodeType.START: "🚪",
        }

        color = colors.get(node.node_type, '#505050')
        icon = icons.get(node.node_type, "?")


        if node.visited:
            color = '#333333'
        elif not node.available:
            color = '#222222'


        node_radius = 20
        outline_width = 3

        if self.game.game_map.get_current_node() == node:
            outline_color = '#00FF00'
            outline_width = 4
        elif node.available:
            outline_color = '#FFFF00'
        else:
            outline_color = '#666666'


        node_oval = self.map_canvas.create_oval(
            x - node_radius, y - node_radius,
            x + node_radius, y + node_radius,
            fill=color,
            outline=outline_color,
            width=outline_width,
            tags=f"node_{node.node_id}"
        )


        self.node_click_map[node_oval] = node.node_id


        self.map_canvas.create_text(
            x, y,
            text=icon,
            font=("Arial", 14),
            tags=f"node_{node.node_id}"
        )


        self.map_canvas.create_text(
            x, y - node_radius - 15,
            text=f"F{node.floor}",
            font=("Courier New", 8),
            fill=self.COLORS['text_secondary'],
            tags=f"node_{node.node_id}"
        )

    def _on_map_canvas_click(self, event):
        """Handle clicks on map canvas nodes."""

        canvas_width = self.map_canvas.winfo_width()
        if canvas_width < 100:
            canvas_width = 800
        map_height = (self.game.game_map.num_floors + 2) * 80


        try:
            scroll_top = self.map_canvas.canvasy(0)
        except:
            scroll_top = 0


        clicked_y = event.y + scroll_top


        for node in self.game.game_map.nodes:

            node_x, node_y = self._calculate_node_position(node, canvas_width, map_height)


            distance = math.sqrt((event.x - node_x)**2 + (clicked_y - node_y)**2)

            if distance < 50:
                if node.available and not node.visited:
                    self._enter_node(node.node_id)
                    return


        available_nodes = self.game.game_map.get_available_nodes()
        if available_nodes:
            best_node = None
            best_distance = float('inf')

            for node in available_nodes:
                node_x, node_y = self._calculate_node_position(node, canvas_width, map_height)
                distance = math.sqrt((event.x - node_x)**2 + (clicked_y - node_y)**2)

                if distance < best_distance:
                    best_distance = distance
                    best_node = node


            if best_node and best_distance < 150:
                self._enter_node(best_node.node_id)

    def _enter_node(self, node_id: int):
        """Enter a map node."""
        if not self.game:
            return

        node = self.game.game_map.nodes[node_id]


        if node.visited:
            return


        if not node.available:
            return


        state, message = self.game.enter_node(node_id)

        if state == GameState.BATTLE:
            self._show_battle()
        elif state == GameState.SHOP:
            self._show_shop()
        elif state == GameState.MAP:

            if message:
                messagebox.showinfo("Event", message)

            for child_id in node.children:
                if child_id < len(self.game.game_map.nodes):
                    self.game.game_map.nodes[child_id].available = True

            if self.game.player and not self.game.player.is_alive:
                self._show_end_screen(False)
                return
            self._show_map()
        elif state == GameState.VICTORY:
            self._show_end_screen(True)
        elif state == GameState.DEFEAT:
            self._show_end_screen(False)



    def _build_battle_screen(self):
        """Build the battle screen."""
        frame = self._create_frame('battle')


        battlefield = tk.Frame(frame, bg=self.COLORS['background'])
        battlefield.pack(fill=tk.X, pady=(6, 0))


        player_panel = tk.Frame(battlefield, bg=self.COLORS['panel_bg'], bd=3, relief=tk.GROOVE)
        player_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=4)

        self.battle_player_class = tk.Label(
            player_panel, text="PLAYER",
            font=("Courier New", 13, "bold"),
            fg=self.COLORS['gold'], bg=self.COLORS['panel_bg'])
        self.battle_player_class.pack(pady=4)

        self.player_avatar = tk.Canvas(player_panel, width=80, height=80,
                                       bg='#1a1010', highlightthickness=0)
        self.player_avatar.pack(pady=4)

        self.battle_player_stats = tk.Label(
            player_panel, text="", font=("Courier New", 9),
            fg=self.COLORS['text_primary'], bg=self.COLORS['panel_bg'], justify=tk.LEFT)
        self.battle_player_stats.pack(pady=3)

        self.battle_stance_label = tk.Label(
            player_panel, text="STANCE: OBSERVATION",
            font=("Courier New", 10, "bold"), fg="#00CCFF", bg=self.COLORS['panel_bg'])
        self.battle_stance_label.pack(pady=3)


        enemy_panel = tk.Frame(battlefield, bg=self.COLORS['panel_bg'], bd=3, relief=tk.GROOVE)
        enemy_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=4)

        self.battle_enemy_name = tk.Label(
            enemy_panel, text="ENEMY",
            font=("Courier New", 13, "bold"),
            fg=self.COLORS['red'], bg=self.COLORS['panel_bg'])
        self.battle_enemy_name.pack(pady=4)

        self.enemy_avatar = tk.Canvas(enemy_panel, width=80, height=80,
                                      bg='#1a1010', highlightthickness=0)
        self.enemy_avatar.pack(pady=4)

        self.battle_enemy_stats = tk.Label(
            enemy_panel, text="", font=("Courier New", 9),
            fg=self.COLORS['text_primary'], bg=self.COLORS['panel_bg'], justify=tk.LEFT)
        self.battle_enemy_stats.pack(pady=3)


        self.card_inspector_frame = tk.Frame(
            frame, bg='#1a1030', bd=3, relief=tk.RAISED)


        insp_header = tk.Frame(self.card_inspector_frame, bg='#2a1050')
        insp_header.pack(fill=tk.X)

        self.insp_title = tk.Label(
            insp_header, text="CARD INSPECTOR",
            font=("Courier New", 12, "bold"),
            fg=self.COLORS['gold'], bg='#2a1050')
        self.insp_title.pack(side=tk.LEFT, padx=10, pady=4)

        tk.Button(
            insp_header, text="✕  Close",
            font=("Courier New", 10),
            bg='#5a1020', fg='#ffffff', cursor="hand2",
            command=self._close_card_inspector
        ).pack(side=tk.RIGHT, padx=8, pady=3)

        insp_body = tk.Frame(self.card_inspector_frame, bg='#1a1030')
        insp_body.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)


        insp_meta = tk.Frame(insp_body, bg='#1a1030')
        insp_meta.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.insp_name = tk.Label(
            insp_meta, text="", font=("Times New Roman", 15, "bold"),
            fg=self.COLORS['gold'], bg='#1a1030', wraplength=220, justify=tk.LEFT)
        self.insp_name.pack(anchor=tk.W)

        self.insp_meta_text = tk.Label(
            insp_meta, text="", font=("Courier New", 10),
            fg=self.COLORS['text_secondary'], bg='#1a1030', justify=tk.LEFT)
        self.insp_meta_text.pack(anchor=tk.W, pady=3)

        self.insp_desc = tk.Label(
            insp_meta, text="", font=("Courier New", 9, "italic"),
            fg='#aaccff', bg='#1a1030', wraplength=220, justify=tk.LEFT)
        self.insp_desc.pack(anchor=tk.W)


        insp_code_frame = tk.Frame(insp_body, bg='#1a1030')
        insp_code_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(insp_code_frame, text="HEROSCRIPT SOURCE:",
                 font=("Courier New", 10, "bold"),
                 fg=self.COLORS['gold'], bg='#1a1030').pack(anchor=tk.W)

        self.insp_code_box = scrolledtext.ScrolledText(
            insp_code_frame,
            font=("Courier New", 12),
            bg='#050818', fg='#88ff88',
            height=5, state=tk.DISABLED,
            relief=tk.FLAT, bd=0,
            wrap=tk.NONE)
        self.insp_code_box.pack(fill=tk.BOTH, expand=True)


        self.battle_hand_label = tk.Label(
            frame,
            text="YOUR HAND  —  Click a card to inspect it",
            font=("Courier New", 11, "bold"),
            fg=self.COLORS['text_primary'], bg=self.COLORS['background'])
        self.battle_hand_label.pack(pady=(4, 0))

        self.hand_canvas = tk.Canvas(
            frame, height=140, bg='#151515', highlightthickness=0)
        self.hand_canvas.pack(fill=tk.X, padx=20, pady=4)
        self.hand_canvas.bind("<Button-1>", self._on_card_click)


        bottom = tk.Frame(frame, bg=self.COLORS['background'])
        bottom.pack(fill=tk.BOTH, expand=True, pady=4)


        code_panel = tk.Frame(bottom, bg=self.COLORS['panel_bg'], bd=2)
        code_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5))

        tk.Label(code_panel, text="CODE SNIPPET",
                 font=("Courier New", 11, "bold"),
                 fg=self.COLORS['gold'], bg=self.COLORS['panel_bg']
                 ).pack(anchor=tk.W, padx=5, pady=2)

        self.battle_code_text = scrolledtext.ScrolledText(
            code_panel, height=5, font=("Courier New", 11),
            bg='#1e140f', fg=self.COLORS['text_primary'], insertbackground='white')
        self.battle_code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        controls = tk.Frame(code_panel, bg=self.COLORS['panel_bg'])
        controls.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(controls, text="Play Card",
                  font=("Courier New", 11, "bold"),
                  bg='#403020', fg=self.COLORS['text_primary'],
                  command=self._play_selected_card
                  ).pack(side=tk.LEFT, padx=5)

        tk.Button(controls, text="Toggle Stance",
                  font=("Courier New", 11, "bold"),
                  bg='#206050', fg='#00CCFF',
                  command=self._toggle_stance_button
                  ).pack(side=tk.LEFT, padx=5)

        tk.Button(controls, text="End Turn",
                  font=("Courier New", 11, "bold"),
                  bg='#304050', fg=self.COLORS['text_primary'],
                  command=self._end_turn
                  ).pack(side=tk.LEFT, padx=5)


        log_panel = tk.Frame(bottom, bg=self.COLORS['panel_bg'], bd=2)
        log_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10))

        tk.Label(log_panel, text="COMPILER & BATTLE LOG",
                 font=("Courier New", 11, "bold"),
                 fg=self.COLORS['blue'], bg=self.COLORS['panel_bg']
                 ).pack(anchor=tk.W, padx=5, pady=2)

        self.battle_log = scrolledtext.ScrolledText(
            log_panel, font=("Courier New", 9),
            bg='#050810', fg='#D0E0FF', height=10)
        self.battle_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _show_battle(self):
        """Update and show the battle screen."""
        if not self.game or not self.game.battle:
            self._show_map()
            return

        self._show_frame('battle')

        self._close_card_inspector()
        self.selected_card_index = None

        self.battle_log_text = "=== COMPILER & BATTLE LOG ===\nBattle started!\n"

        self._update_battle_display()

    def _update_battle_display(self):
        """Update all battle UI elements."""
        if not self.game or not self.game.battle:
            return

        battle = self.game.battle
        player = battle.player
        enemy = battle.enemy


        self.battle_player_class.config(text=player.char_class.upper())


        energy_pips = "⚡" * player.energy + "○" * (player.max_energy - player.energy)
        player_stats = (f"HP: {player.hp}/{player.max_hp}\n"
                       f"Energy: {energy_pips}\n"
                       f"Block: {'🛡️' * min(player.block, 5)} {player.block}\n"
                       f"Strength: {'⚔️' * min(player.strength, 5)} {player.strength}")
        self.battle_player_stats.config(text=player_stats)


        stance_name = "INTERVENTION" if player.current_stance == Stance.INTERVENTION else "OBSERVATION"
        stance_color = "#FF6600" if player.current_stance == Stance.INTERVENTION else "#00CCFF"
        self.battle_stance_label.config(text=f"STANCE: {stance_name}", fg=stance_color)


        self.player_avatar.delete("all")


        player_sprite = sprite_manager.get_class_sprite(player.char_class)
        if player_sprite and PIL_AVAILABLE:
            self.player_sprite_ref = player_sprite
            self.player_avatar.create_image(40, 40, image=player_sprite)
        else:

            class_colors = {
                "Ironclad": "#C0402C", "Silent": "#4AA050", "Defect": "#4080C8",
                "Watcher": "#A050D0", "Glass Cannon": "#FF4444",
                "Necromancer": "#4A0080", "Chronomancer": "#0080FF"
            }
            color = class_colors.get(player.char_class, "#EEEEEE")
            self.player_avatar.create_oval(10, 5, 70, 55, fill=color, outline="#FFFFFF", width=2)


        hp_pct = player.hp / player.max_hp if player.max_hp > 0 else 0
        hp_color = "#00FF00" if hp_pct > 0.5 else "#FFAA00" if hp_pct > 0.25 else "#FF0000"
        self.player_avatar.create_rectangle(5, 62, 75, 72, fill="#333333", outline="#555555")
        self.player_avatar.create_rectangle(5, 62, 5 + int(70 * hp_pct), 72, fill=hp_color, outline="")
        self.player_avatar.create_text(40, 67, text=f"{player.hp}/{player.max_hp}", fill="white", font=("Courier New", 7, "bold"))


        self.battle_enemy_name.config(text=enemy.name.upper())

        enemy_intent = enemy.get_intent()
        intent_icon = "⚔️" if enemy_intent.get("type") == "attack" else "✨"
        debuff_str = ""
        if enemy.debuffs:
            debuff_str = "\n" + "  ".join(
                f"[{d.name[:3].upper()} {d.duration}t]" for d in enemy.debuffs
            )
        enemy_stats = (f"HP: {enemy.hp}/{enemy.max_hp}\n"
                      f"Intent: {intent_icon} {enemy_intent.get('damage', '?')} dmg"
                      f"{debuff_str}")
        self.battle_enemy_stats.config(text=enemy_stats)


        self.enemy_avatar.delete("all")


        enemy_sprite = sprite_manager.get_enemy_sprite(enemy.name)
        if not enemy_sprite:

            enemy_type_str = "normal"
            if enemy.enemy_type == EnemyType.BOSS:
                enemy_type_str = "boss"
            elif enemy.enemy_type == EnemyType.ELITE:
                enemy_type_str = "elite"
            elif enemy.enemy_type == EnemyType.MINION:
                enemy_type_str = "minion"
            enemy_sprite = sprite_manager.get_enemy_sprite(enemy_type_str)

        if enemy_sprite and PIL_AVAILABLE:
            self.enemy_sprite_ref = enemy_sprite
            self.enemy_avatar.create_image(40, 40, image=enemy_sprite)
        else:

            enemy_color = "#CC3333"
            if enemy.enemy_type == EnemyType.BOSS:
                enemy_color = "#8B008B"
            elif enemy.enemy_type == EnemyType.ELITE:
                enemy_color = "#DAA520"
            self.enemy_avatar.create_polygon(15, 55, 40, 5, 65, 5, 65, 55, fill=enemy_color, outline="#FFFFFF", width=2)


        enemy_hp_pct = enemy.hp / enemy.max_hp if enemy.max_hp > 0 else 0
        enemy_hp_color = "#FF4444" if enemy_hp_pct > 0.5 else "#FF8800" if enemy_hp_pct > 0.25 else "#AAAAAA"
        self.enemy_avatar.create_rectangle(5, 62, 75, 72, fill="#333333", outline="#555555")
        self.enemy_avatar.create_rectangle(5, 62, 5 + int(70 * enemy_hp_pct), 72, fill=enemy_hp_color, outline="")
        self.enemy_avatar.create_text(40, 67, text=f"{enemy.hp}/{enemy.max_hp}", fill="white", font=("Courier New", 7, "bold"))


        self._draw_hand()

    def _close_card_inspector(self):
        """Hide the card inspector panel."""
        self.card_inspector_frame.pack_forget()

    def _show_card_inspector(self, card):
        """Populate and show the card inspector panel above the hand."""

        type_colors = {
            'attack':       '#8B0000',
            'defense':      '#1B5E20',
            'power':        '#4A148C',
            'skill':        '#01579B',
            'attack_power': '#B71C1C',
        }
        rarity_colors = {
            'common':    '#aaaaaa',
            'uncommon':  '#55cc55',
            'rare':      '#5599ff',
            'legendary': '#ff9900',
        }
        band_color = type_colors.get(card.card_type, '#333333')
        rar_color  = rarity_colors.get(card.rarity, '#aaaaaa')

        self.insp_title.config(
            text=f"  ⟨ CARD INSPECTOR ⟩  —  {card.name}",
            bg='#2a1050')

        self.insp_name.config(
            text=card.name,
            fg=self.COLORS['gold'])

        type_label = card.card_type.replace('_', '+').upper()
        self.insp_meta_text.config(
            text=(f"Type:   {type_label}\n"
                  f"Cost:   {card.energy_cost} Energy\n"
                  f"Rarity: {card.rarity.upper()}"),
            fg=rar_color)

        self.insp_desc.config(text=card.description)


        self.insp_code_box.config(state=tk.NORMAL)
        self.insp_code_box.delete("1.0", tk.END)
        self.insp_code_box.insert(tk.END, card.code)
        self.insp_code_box.config(state=tk.DISABLED)



        self.card_inspector_frame.pack(
            fill=tk.X, padx=20, pady=(0, 4),
            before=self.battle_hand_label)

    def _draw_hand(self):
        """Draw the player's hand on the hand canvas."""
        if not self.game or not self.game.battle:
            return

        self.hand_canvas.delete("all")
        hand = self.game.battle.player.hand


        card_w  = 170
        card_h  = 130
        gap     =  10
        total_w = len(hand) * card_w + (len(hand) - 1) * gap if hand else card_w
        canvas_w = self.hand_canvas.winfo_width() or 900
        start_x  = max(10, (canvas_w - total_w) // 2)


        type_colors = {
            'attack':       '#6B0000',
            'defense':      '#1B4E20',
            'power':        '#3A0870',
            'skill':        '#014070',
            'attack_power': '#8B1010',
        }
        rarity_outline = {
            'common':    '#888888',
            'uncommon':  '#44aa44',
            'rare':      '#4477dd',
            'legendary': '#dd8800',
        }

        for idx, card in enumerate(hand):
            x = start_x + idx * (card_w + gap)
            y = 5

            is_selected = (self.selected_card_index == idx)
            hdr_color  = type_colors.get(card.card_type, '#333333')
            out_color  = '#00FF88' if is_selected else rarity_outline.get(card.rarity, '#888888')
            body_color = '#302010' if is_selected else '#1e1408'
            out_width  = 3 if is_selected else 2


            self.hand_canvas.create_rectangle(
                x, y, x + card_w, y + card_h,
                fill=body_color, outline=out_color,
                width=out_width, tags=f"card_{idx}")


            self.hand_canvas.create_rectangle(
                x, y, x + card_w, y + 22,
                fill=hdr_color, outline="", tags=f"card_{idx}")


            self.hand_canvas.create_text(
                x + card_w // 2, y + 11,
                text=card.name,
                fill="#FFFFFF", font=("Courier New", 8, "bold"),
                anchor="center", tags=f"card_{idx}")


            self.hand_canvas.create_oval(
                x + card_w - 22, y + 1,
                x + card_w - 2,  y + 21,
                fill="#222244", outline="#aaaaff", width=1,
                tags=f"card_{idx}")
            self.hand_canvas.create_text(
                x + card_w - 12, y + 11,
                text=str(card.energy_cost),
                fill="#aaaaff", font=("Courier New", 8, "bold"),
                anchor="center", tags=f"card_{idx}")


            desc_short = card.description if len(card.description) <= 28 else card.description[:26] + "…"
            self.hand_canvas.create_text(
                x + 6, y + 28,
                text=desc_short,
                fill="#cccccc", font=("Courier New", 7),
                anchor="nw", tags=f"card_{idx}")


            code_lines = card.code.strip().split('\n')
            preview_lines = code_lines[:3]
            if len(code_lines) > 3:
                preview_lines.append("  ...")
            preview = '\n'.join(
                (ln[:24] + '…' if len(ln) > 24 else ln) for ln in preview_lines
            )
            self.hand_canvas.create_text(
                x + 6, y + 48,
                text=preview,
                fill="#88ff88", font=("Courier New", 7),
                anchor="nw", tags=f"card_{idx}")


            if not is_selected:
                self.hand_canvas.create_text(
                    x + card_w // 2, y + card_h - 8,
                    text="🔍 click to inspect",
                    fill="#555555", font=("Courier New", 6),
                    anchor="center", tags=f"card_{idx}")
            else:
                self.hand_canvas.create_text(
                    x + card_w // 2, y + card_h - 8,
                    text="✓ SELECTED",
                    fill="#00FF88", font=("Courier New", 7, "bold"),
                    anchor="center", tags=f"card_{idx}")

    def _on_card_click(self, event):
        """Handle card click — select it AND open the card inspector."""
        items = self.hand_canvas.find_withtag("current")
        if not items:
            return

        tags = self.hand_canvas.gettags(items[0])
        for tag in tags:
            if tag.startswith("card_"):
                try:
                    idx = int(tag.split("_")[1])
                    if not (self.game and idx < len(self.game.battle.player.hand)):
                        break

                    card = self.game.battle.player.hand[idx]


                    if self.selected_card_index == idx:
                        self.selected_card_index = None
                        self._close_card_inspector()
                    else:
                        self.selected_card_index = idx
                        self.expected_code = card.code

                        self.battle_code_text.delete("1.0", tk.END)

                        self._show_card_inspector(card)

                        hint_map = {
                            'attack':       "Type: bolt dmg ~ <number>.",
                            'attack_power': "Type: bolt dmg ~ <number>.  bolt pow ~ <number>.",
                            'defense':      "Type: bolt def ~ <number>.",
                            'skill':        "Type: bolt heal ~ <number>.",
                            'power':        "Type: bolt pow ~ <number>.",
                        }
                        hint = hint_map.get(card.card_type, "Type valid HEROSCRIPT code.")
                        self._log_message(
                            f"[CARD SELECTED] {card.name} ({card.energy_cost}E) — {hint}",
                            "system")

                    self._draw_hand()
                    break
                except Exception:
                    pass

    def _toggle_stance_button(self):
        """Handle stance toggle button click."""
        if not self.game or not self.game.battle:
            return

        player = self.game.battle.player


        if player.toggle_stance():

            stance_name = "INTERVENTION" if player.current_stance == Stance.INTERVENTION else "OBSERVATION"
            stance_color = "#FF6600" if player.current_stance == Stance.INTERVENTION else "#00CCFF"


            self.battle_stance_label.config(text=f"STANCE: {stance_name}", fg=stance_color)


            modifier_str = "+30% damage, +30% damage taken" if player.current_stance == Stance.INTERVENTION else "-30% damage, -30% damage taken"
            self._log_message(f"✓ Stance toggled to {stance_name} ({modifier_str})", "battle")
        else:

            self._log_message("Stance is locked! Cannot toggle this turn.", "battle")

        self._update_battle_display()

    def _play_selected_card(self):
        """Play the card using the user's typed code in the code editor.

        Flow:
        1. Read the code from the code editor text box
        2. Execute the code using execute_card_code()
        3. Validate code matches card type
        4. Apply the results (damage, block, heal, strength)
        5. Remove a card from hand (paying the card)
        """
        if not self.game or not self.game.battle:
            self._log_message("Not in battle!", "battle")
            return


        code = self.battle_code_text.get("1.0", tk.END).strip()


        card_index = self.selected_card_index
        if card_index is None or card_index >= len(self.game.battle.player.hand):
            self._log_message("Select a card from your hand first!", "battle")
            return

        card = self.game.battle.player.hand[card_index]


        if card.energy_cost > self.game.battle.player.energy:
            self._log_message(f"Not enough energy! Need {card.energy_cost}, have {self.game.battle.player.energy}", "battle")
            return


        is_attack_card       = card.card_type in ('attack', 'attack_power')
        is_defense_card      = card.card_type == 'defense'
        is_power_card        = card.card_type == 'power'
        is_skill_card        = card.card_type == 'skill'
        is_attack_power_card = card.card_type == 'attack_power'


        if not code:
            self._show_code_error(card, "⚠️ ATTACK FAILED — No code provided! You must type HEROSCRIPT code.", code)
            return







        has_dmg    = bool(re.search(r'bolt\s+dmg\s*~',    code, re.IGNORECASE))
        has_def    = bool(re.search(r'bolt\s+def\s*~',    code, re.IGNORECASE))
        has_heal   = bool(re.search(r'bolt\s+heal\s*~',   code, re.IGNORECASE))
        has_pow    = bool(re.search(r'bolt\s+pow\s*~',    code, re.IGNORECASE))
        has_scroll = bool(re.search(r'scroll\s+\w+\s*~',  code, re.IGNORECASE))
        has_repeat = bool(re.search(r'\brepeat\b',         code, re.IGNORECASE))
        has_test   = bool(re.search(r'\btest\b',           code, re.IGNORECASE))

        code_valid     = False
        code_error_msg = ""

        if is_attack_power_card:
            if has_dmg and has_pow:
                code_valid = True
            elif not has_dmg:
                code_error_msg = "⚠️ FAILED — attack+power card requires 'bolt dmg ~ <number>' in your code!"
            else:
                code_error_msg = "⚠️ FAILED — attack+power card requires 'bolt pow ~ <number>' in your code!"

        elif is_attack_card:

            if has_dmg:
                code_valid = True

                if has_def:
                    code_valid     = False
                    code_error_msg = "⚠️ FAILED — attack card cannot contain 'bolt def'. Remove it."
                elif has_heal:
                    code_valid     = False
                    code_error_msg = "⚠️ FAILED — attack card cannot contain 'bolt heal'. Remove it."
            else:

                if has_repeat:

                    if re.search(r'repeat\s+\d+\s*:\s*\n\s+bolt\s+dmg\s*~', code, re.IGNORECASE):
                        code_valid = True
                    else:
                        code_error_msg = ("⚠️ FAILED — repeat loop on attack card must contain "
                                          "'bolt dmg ~ <number>' indented inside the loop body.")
                elif has_test:

                    if re.search(r'bolt\s+dmg\s*~', code, re.IGNORECASE):
                        code_valid = True
                    else:
                        code_error_msg = ("⚠️ FAILED — test block on attack card must contain "
                                          "'bolt dmg ~ <number>' in at least one branch.")
                else:
                    code_error_msg = ("⚠️ FAILED — attack card requires 'bolt dmg ~ <number>' "
                                      "(or a repeat/test block containing bolt dmg).")

        elif is_defense_card:
            if has_def:
                code_valid = True
                if has_dmg or has_heal or has_pow:
                    code_valid     = False
                    code_error_msg = "⚠️ FAILED — defense cards only accept 'bolt def ~ <number>'."
            else:
                code_error_msg = "⚠️ FAILED — defense card requires 'bolt def ~ <number>' in your code!"

        elif is_power_card:
            if has_pow:
                code_valid = True
                if has_dmg or has_def or has_heal:
                    code_valid     = False
                    code_error_msg = "⚠️ FAILED — power cards only accept 'bolt pow ~ <number>'."
            else:
                code_error_msg = "⚠️ FAILED — power card requires 'bolt pow ~ <number>' in your code!"

        elif is_skill_card:
            if has_heal:
                code_valid = True
                if has_dmg or has_def or has_pow:
                    code_valid     = False
                    code_error_msg = "⚠️ FAILED — heal/skill cards only accept 'bolt heal ~ <number>'."
            else:
                code_error_msg = "⚠️ FAILED — heal/skill card requires 'bolt heal ~ <number>' in your code!"

        else:
            if has_dmg or has_def or has_heal or has_pow:
                code_valid = True
            else:
                code_error_msg = "⚠️ FAILED — use bolt dmg/def/heal/pow ~ <number>."

        if not code_valid:
            self._show_code_error(card, code_error_msg, code)
            return


        self.game.battle.player.energy -= card.energy_cost

        result = execute_card_code(code, enemy=self.game.battle.enemy)

        if not result.get('success', True) and result.get('error'):
            self._show_code_error(card, f"⚠️ ATTACK FAILED — Code execution error: {result.get('error')}", code)
            self.game.battle.player.energy += card.energy_cost
            return


        damage_rolls   = result.get('rolls', [])
        defense_rolls  = result.get('defense_rolls', [])
        heal_rolls     = result.get('heal_rolls', [])
        strength_rolls = result.get('strength_rolls', [])
        base_damage    = result.get('damage', 0)
        block          = result.get('block', 0)
        heal           = result.get('heal', 0)
        strength       = result.get('strength', 0)



        if is_attack_power_card:

            block = 0
            heal  = 0

        elif is_attack_card:

            block    = 0
            heal     = 0
            strength = 0

            defense_rolls  = []
            heal_rolls     = []
            strength_rolls = []

        elif is_defense_card:

            base_damage    = 0
            damage_rolls   = []
            heal           = 0
            strength       = 0
            heal_rolls     = []
            strength_rolls = []

        elif is_power_card:

            base_damage   = 0
            damage_rolls  = []
            block         = 0
            defense_rolls = []
            heal          = 0
            heal_rolls    = []

        elif is_skill_card:

            base_damage    = 0
            damage_rolls   = []
            block          = 0
            defense_rolls  = []
            strength       = 0
            strength_rolls = []


        if is_defense_card:
            for relic in self.game.battle.player.equipped_relics:
                block += relic.get_bonus('block')


        relic_damage_bonus = 0
        if is_attack_card or is_attack_power_card:
            for relic in self.game.battle.player.equipped_relics:
                relic_damage_bonus += relic.get_bonus('damage')


        if block > 0:
            self.game.battle.player.block += block


        if heal > 0:
            self.game.battle.player.heal(heal)


        if strength > 0:
            self.game.battle.player.strength += strength


        self.game.battle.player.hand.pop(card_index)
        self.game.battle.player.discard_pile.append(card)


        if (is_attack_card or is_attack_power_card) and self.game.battle.player.char_class == "Silent":
            self.game.battle.player.gain_block(1)



        if is_attack_card or is_attack_power_card:
            final_damage = base_damage + self.game.battle.player.strength + relic_damage_bonus
        else:
            final_damage = 0


        self._log_message(f">>> EXECUTING CODE: {code[:50]}{'...' if len(code) > 50 else ''}", "lexical")


        if damage_rolls:
            roll_str = ' + '.join(str(r) for r in damage_rolls)
            self._log_message(f"--- DAMAGE ROLLS: {roll_str} ---", "system")
            self._log_message(f"Base damage: {base_damage}", "rolls")


        if defense_rolls:
            def_str = ' + '.join(str(r) for r in defense_rolls)
            self._log_message(f"--- DEFENSE ROLLS: {def_str} ---", "system")
            self._log_message(f"Block gained: {block}", "rolls")


        if heal_rolls:
            heal_str = ' + '.join(str(r) for r in heal_rolls)
            self._log_message(f"--- HEAL ROLLS: {heal_str} ---", "system")
            self._log_message(f"Healed for: {heal}", "rolls")


        if strength_rolls:
            pow_str = ' + '.join(str(r) for r in strength_rolls)
            self._log_message(f"--- STRENGTH ROLLS: {pow_str} ---", "system")
            self._log_message(f"Strength gained: {strength}", "rolls")


        self._log_message("--- LEXICAL ANALYSIS ---", "system")
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        unknown_count = 0

        for t in tokens:
            if t.type in (TokenType.WHITESPACE, TokenType.NEWLINE, TokenType.COMMENT):
                continue
            label = t.type.name
            if t.type == TokenType.DATATYPE:
                label = 'DATATYPE'
            elif t.type == TokenType.KEYWORD:
                label = 'KEYWORD'
            elif t.type == TokenType.IDENTIFIER:
                label = 'IDENTIFIER'
            elif t.type in (TokenType.ASSIGN_OP, TokenType.FIXED_ASSIGN):
                label = 'ASSIGN_OPERATOR'
            elif t.type == TokenType.DELIMITER:
                label = 'DELIMITER'
            elif t.type == TokenType.OPERATOR:
                label = 'OPERATOR'
            elif t.type == TokenType.NUMERIC:
                label = 'NUMERIC_LITERAL'
            elif t.type == TokenType.UNKNOWN:
                unknown_count += 1
                label = 'UNKNOWN'
            self._log_message(f"[LEXER] Found '{t.value}' -> {label}", "lexical")

        self._log_message(f"✓ Lexical Complete. {unknown_count} Unknown Tokens.", "lexical")


        self._log_message("--- SYNTAX ANALYSIS ---", "system")
        self._log_message("[PARSER] Checking structure...", "syntax")
        self._log_message("[PARSER] Validating syntax...", "syntax")
        self._log_message("✓ Syntax OK.", "syntax")


        self._log_message("--- SEMANTIC ANALYSIS ---", "system")
        self._log_message("[SEMANTICS] Type checking...", "semantic")
        self._log_message("[SEMANTICS] Binding to memory...", "semantic")
        self._log_message("✓ Semantics OK.", "semantic")


        table = "SYMBOL TABLE:\n" + "=" * 35 + "\n"
        table += " NAME      TYPE         LVL    WIDTH    OFFSET\n"
        table += "-" * 35 + "\n"

        decl_pattern = r'bolt\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        declarations = re.findall(decl_pattern, code)

        offset = 0
        width = 4

        for var_name in declarations:
            table += f" {var_name:<9} bolt      0     {width}      {offset}\n"
            offset += width

        table += "-" * 35 + "\n"
        table += f"Total Memory: {offset} Bytes\n"
        table += "=" * 35
        self._log_message(table, "symbols")


        if block > 0:
            self._log_message(f"✓ Gained {block} block!", "battle")

        if heal > 0:
            self._log_message(f"✓ Healed for {heal} HP!", "battle")

        if strength > 0:
            self._log_message(f"✓ Gained {strength} strength!", "battle")


        if (is_attack_card or is_attack_power_card) and final_damage > 0 and self.game.battle.enemy.is_alive:

            if self.game.battle.player.char_class == "Glass Cannon" and random.random() < 0.25:
                final_damage = int(final_damage * 1.5)
                self._log_message(f"⚡ CRITICAL HIT! Damage: {final_damage}", "battle")

            self.game.battle.enemy.take_damage(final_damage)
            self._log_message(f"⚔️ Dealt {final_damage} damage to {self.game.battle.enemy.name}!", "battle")


        debuffs_applied = result.get('debuffs', [])
        for debuff in debuffs_applied:
            self.game.battle.enemy.apply_debuff(debuff)
            self._log_message(
                f"☠️ Applied {debuff.name} to {self.game.battle.enemy.name} "
                f"for {debuff.duration} turn(s)!", "battle")

        if debuffs_applied and final_damage == 0:
            self._log_message(f"💀 {self.game.battle.enemy.name} is now afflicted!", "battle")


        if not self.game.battle.enemy.is_alive and not self.game.battle.is_over:
            self.game.battle._on_victory()


        if self.game.battle.is_over:
            player_won = self.game.battle.player_won
            self.selected_card_index = None
            self.game.end_battle(player_won)
            if self.game.state == GameState.VICTORY:
                self._show_end_screen(True)
            elif player_won:
                self._show_reward_screen()
            else:
                self._show_end_screen(False)
            return

        self._log_message("✓ Card played successfully!", "battle")
        self.selected_card_index = None
        self._close_card_inspector()
        self._update_battle_display()


    def _end_turn(self):
        """End the player's turn."""
        if not self.game or not self.game.battle:
            return

        result = self.game.battle.end_player_turn()

        if result.get("extra_turn"):
            self._log_message("⏰ TIME WARP! Extra turn!", "battle")

        self._log_message(result.get("log", ""), "battle")


        if self.game.battle and self.game.battle.is_over:
            player_won = self.game.battle.player_won
            self.game.end_battle(player_won)

            if self.game.state == GameState.VICTORY:
                self._show_end_screen(True)
            elif player_won:
                self._show_reward_screen()
            else:
                self._show_end_screen(False)
            return

        self.selected_card_index = None
        self._close_card_inspector()
        self._update_battle_display()

    def _log_message(self, message: str, log_type: str = "battle"):
        """Add a message to the unified log."""
        if not hasattr(self, 'battle_log_text'):
            self.battle_log_text = "=== COMPILER & BATTLE LOG ===\n"


        if log_type == "battle":
            formatted = f"[BATTLE] {message}\n"
        elif log_type == "lexical":
            formatted = f"[LEXICAL] {message}\n"
        elif log_type == "rolls":
            formatted = f"[ROLLING] [ROLLS] {message}\n"
        elif log_type == "semantic":
            formatted = f"[SEMANTIC] {message}\n"
        elif log_type == "syntax":
            formatted = f"[SYNTAX] {message}\n"
        elif log_type == "symbols":
            formatted = f"[SYMBOLS] {message}\n"
        elif log_type == "player":
            formatted = f"[PLAYER] {message}\n"
        elif log_type == "system":
            formatted = f"[SYSTEM] {message}\n"
        else:
            formatted = f"{message}\n"

        self.battle_log_text += formatted


        self.battle_log.config(state=tk.NORMAL)
        self.battle_log.delete("1.0", tk.END)
        self.battle_log.insert(tk.END, self.battle_log_text)
        self.battle_log.see(tk.END)
        self.battle_log.config(state=tk.DISABLED)

    def _show_code_error(self, card, error_message: str, code: str):
        """
        Full compiler pipeline error display.
        Runs real lexical, syntax, and semantic analysis on the typed code
        and reports every error found at each stage, informed by the HEROSCRIPT cheat sheet.
        """

        VALID_BATTLE_VARS = {'dmg', 'def', 'heal', 'pow'}


        REQUIRED_VAR = {
            'attack':       'dmg',
            'attack_power': 'dmg',
            'defense':      'def',
            'skill':        'heal',
            'power':        'pow',
        }


        self._log_message("=" * 50, "system")
        self._log_message(f"⚠️  CARD FAILED: {error_message}", "battle")
        self._log_message(f"    Card: {card.name}  |  Type: {card.card_type}  |  Cost: {card.energy_cost}E", "battle")
        self._log_message(f"    Code entered: {code if code else '(empty)'}", "battle")
        self._log_message("=" * 50, "system")



        self._log_message("--- STAGE 1: LEXICAL ANALYSIS ---", "system")

        if not code:
            self._log_message("[LEXER] ✗ ERROR: No code provided — the code box is empty.", "lexical")
            self._log_message("[LEXER] ✗ Lexical FAILED: Cannot tokenize empty input.", "lexical")

            self._show_expected_format(card)
            return

        lex_errors = []
        tokens = []
        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()

            meaningful = [t for t in tokens if t.type not in
                          (TokenType.NEWLINE, TokenType.COMMENT, TokenType.EOF)]

            for t in meaningful:
                token_label = {
                    TokenType.KEYWORD:      'KEYWORD',
                    TokenType.DATATYPE:     'DATATYPE',
                    TokenType.IDENTIFIER:   'IDENTIFIER',
                    TokenType.ASSIGN_OP:    'ASSIGN_OP (~)',
                    TokenType.FIXED_ASSIGN: 'FIXED_ASSIGN (~~)',
                    TokenType.NUMERIC:      'NUMERIC_LITERAL',
                    TokenType.OPERATOR:     'OPERATOR',
                    TokenType.DELIMITER:    'DELIMITER (.)',
                    TokenType.STRING:       'STRING_LITERAL',
                    TokenType.BOOLEAN:      'BOOLEAN',
                    TokenType.LPAREN:       'LPAREN',
                    TokenType.RPAREN:       'RPAREN',
                    TokenType.UNKNOWN:      'UNKNOWN ← ERROR',
                }.get(t.type, t.type.name)

                if t.type == TokenType.UNKNOWN:
                    msg = (f"[LEXER] ✗ ERROR at {t.line}:{t.column} — "
                           f"Unknown character '{t.value}'. "
                           f"HEROSCRIPT only allows: bolt/scroll/flag/char, identifiers, numbers, ~, .")
                    self._log_message(msg, "lexical")
                    lex_errors.append(msg)
                else:
                    self._log_message(
                        f"[LEXER]   Token '{t.value}' → {token_label}  (line {t.line}, col {t.column})",
                        "lexical")


            has_delimiter = any(t.type == TokenType.DELIMITER and t.value == '.' for t in tokens)
            if not has_delimiter:
                msg = "[LEXER] ✗ ERROR: Missing statement terminator '.' — every HEROSCRIPT statement must end with a period."
                self._log_message(msg, "lexical")
                lex_errors.append(msg)


            first_real = next((t for t in meaningful if t.type != TokenType.EOF), None)
            if first_real and first_real.type not in (TokenType.DATATYPE, TokenType.KEYWORD):
                msg = (f"[LEXER] ✗ ERROR at {first_real.line}:{first_real.column} — "
                       f"Statement must start with a datatype keyword (bolt, scroll, flag, char) "
                       f"or a control keyword (speak, repeat, test). Got '{first_real.value}'.")
                self._log_message(msg, "lexical")
                lex_errors.append(msg)

            if lex_errors:
                self._log_message(f"[LEXER] ✗ Lexical FAILED — {len(lex_errors)} error(s) found.", "lexical")
            else:
                self._log_message(f"[LEXER] ✓ Lexical OK — {len(meaningful)} token(s) recognised.", "lexical")

        except LexerError as e:
            msg = f"[LEXER] ✗ FATAL at {e.line}:{e.column} — {e.message}"
            self._log_message(msg, "lexical")
            lex_errors.append(msg)
            self._log_message("[LEXER] ✗ Lexical FAILED — cannot continue.", "lexical")
            self._show_expected_format(card)
            return





        self._log_message("--- STAGE 2: SYNTAX ANALYSIS ---", "system")

        syn_errors = []
        ast = []

        try:
            parser = Parser(tokens)
            ast = parser.parse()


            for stmt in ast:
                stype = stmt.get('type')

                if stype == 'declaration':
                    var    = stmt.get('name', '')
                    assign = stmt.get('assign_op')
                    value  = stmt.get('value', {})
                    dtype  = stmt.get('datatype', '')


                    if assign == '~~':
                        msg = (f"[PARSER] ✗ ERROR: Variable '{var}' uses '~~' (equality check) "
                               f"instead of '~' (dice roll assignment). "
                               f"Use: bolt {var} ~ <number>.")
                        self._log_message(msg, "syntax")
                        syn_errors.append(msg)


                    if value and value.get('type') == 'literal':
                        msg = (f"[PARSER] ✗ ERROR: Value for '{var}' is an unresolvable literal "
                               f"'{value.get('value')}'. Expected a number (e.g. 6) or "
                               f"dice expression (e.g. 4+4).")
                        self._log_message(msg, "syntax")
                        syn_errors.append(msg)

                    if not assign:
                        msg = (f"[PARSER] ✗ ERROR: Variable '{var}' has no assignment operator. "
                               f"Use: bolt {var} ~ <number>.")
                        self._log_message(msg, "syntax")
                        syn_errors.append(msg)

                elif stype == 'unknown':
                    msg = (f"[PARSER] ✗ ERROR: Unrecognised statement '{stmt.get('value', '')}'. "
                           f"Check spelling — valid keywords: bolt, scroll, flag, speak, repeat, test.")
                    self._log_message(msg, "syntax")
                    syn_errors.append(msg)

            if not ast:
                msg = "[PARSER] ✗ ERROR: No valid statements parsed from the code."
                self._log_message(msg, "syntax")
                syn_errors.append(msg)

            if syn_errors:
                self._log_message(f"[PARSER] ✗ Syntax FAILED — {len(syn_errors)} error(s) found.", "syntax")
            else:
                self._log_message("[PARSER] ✓ Syntax OK — statement structure is valid.", "syntax")

        except ParserError as e:
            msg = f"[PARSER] ✗ FATAL: {str(e)}"
            self._log_message(msg, "syntax")
            syn_errors.append(msg)
            self._log_message("[PARSER] ✗ Syntax FAILED — cannot continue.", "syntax")







        self._log_message("--- STAGE 3: SEMANTIC ANALYSIS ---", "system")

        sem_errors = []
        seen_vars = set()

        for stmt in ast:
            if stmt.get('type') != 'declaration':
                continue

            var   = stmt.get('name', '')
            dtype = stmt.get('datatype', '')
            value = stmt.get('value', {})


            if dtype == 'bolt' and var not in VALID_BATTLE_VARS:
                msg = (f"[SEMANTICS] ✗ ERROR: '{var}' is not a valid battle variable. "
                       f"Valid names are: dmg (damage), def (block/defense), "
                       f"heal (healing), pow (strength). "
                       f"Got: '{var}'.")
                self._log_message(msg, "semantic")
                sem_errors.append(msg)
                continue


            required = REQUIRED_VAR.get(card.card_type)
            if required and var != required:
                friendly = {
                    'dmg':  'bolt dmg ~ <number>.  (deals damage)',
                    'def':  'bolt def ~ <number>.  (gives block)',
                    'heal': 'bolt heal ~ <number>. (restores HP)',
                    'pow':  'bolt pow ~ <number>.  (gains strength)',
                }
                msg = (f"[SEMANTICS] ✗ TYPE MISMATCH: Card type '{card.card_type}' requires "
                       f"variable '{required}', but you wrote '{var}'. "
                       f"Correct statement: {friendly.get(required, required)}")
                self._log_message(msg, "semantic")
                sem_errors.append(msg)


            if card.card_type == 'attack_power' and var == 'dmg':
                has_pow_decl = any(
                    s.get('name') == 'pow'
                    for s in ast if s.get('type') == 'declaration'
                )
                if not has_pow_decl:
                    msg = ("[SEMANTICS] ✗ MISSING STATEMENT: attack+power card needs both "
                           "'bolt dmg ~ <number>.' AND 'bolt pow ~ <number>.' — "
                           "the 'bolt pow' line is absent.")
                    self._log_message(msg, "semantic")
                    sem_errors.append(msg)


            if var in seen_vars:
                msg = (f"[SEMANTICS] ✗ ERROR: Variable '{var}' is declared more than once. "
                       f"Each battle variable may only be declared once per card.")
                self._log_message(msg, "semantic")
                sem_errors.append(msg)
            seen_vars.add(var)


            if value:
                val_type = value.get('type')
                if val_type == 'number' and value.get('value', 1) <= 0:
                    msg = (f"[SEMANTICS] ✗ ERROR: Value for '{var}' is {value.get('value')} "
                           f"— must be a positive number (≥ 1).")
                    self._log_message(msg, "semantic")
                    sem_errors.append(msg)


            if dtype != 'bolt' and var in VALID_BATTLE_VARS:
                msg = (f"[SEMANTICS] ✗ TYPE ERROR: Battle variable '{var}' must use "
                       f"datatype 'bolt' (integer). You used '{dtype}'. "
                       f"Correct: bolt {var} ~ <number>.")
                self._log_message(msg, "semantic")
                sem_errors.append(msg)


        bolt_decls = [s for s in ast if s.get('type') == 'declaration' and s.get('datatype') == 'bolt']
        if not bolt_decls:
            msg = ("[SEMANTICS] ✗ ERROR: No 'bolt' declarations found. "
                   "Every card needs at least one bolt statement, e.g.: bolt dmg ~ 6.")
            self._log_message(msg, "semantic")
            sem_errors.append(msg)

        if sem_errors:
            self._log_message(f"[SEMANTICS] ✗ Semantic FAILED — {len(sem_errors)} error(s) found.", "semantic")
        else:
            self._log_message("[SEMANTICS] ✓ Semantics OK — all variable types and names are valid.", "semantic")


        self._log_message("--- SYMBOL TABLE ---", "system")
        table  = " NAME      TYPE    VALID?   REQUIRED?  OFFSET\n"
        table += "-" * 48 + "\n"
        offset = 0
        required_var = REQUIRED_VAR.get(card.card_type, '?')
        for stmt in ast:
            if stmt.get('type') != 'declaration':
                continue
            var   = stmt.get('name', '?')
            dtype = stmt.get('datatype', '?')
            valid_flag    = "✓ YES" if var in VALID_BATTLE_VARS else "✗ NO "
            required_flag = "✓ YES" if var == required_var     else "✗ NO "
            table += f" {var:<9} {dtype:<7} {valid_flag}    {required_flag}   {offset}\n"
            offset += 4
        if offset == 0:
            table += " (no declarations found)\n"
        table += "-" * 48 + "\n"
        table += f" Total: {offset} bytes  |  Card expects: bolt {required_var} ~ <number>.\n"
        self._log_message(table, "symbols")


        self._show_expected_format(card)

    def _show_expected_format(self, card):
        """Print the correct HEROSCRIPT format for this card type."""
        self._log_message("--- CORRECT HEROSCRIPT FORMAT FOR THIS CARD ---", "system")
        fmt = {
            'attack': (
                "Simple attack:\n"
                "    bolt dmg ~ 6.\n\n"
                "Dice pool (N * M = NdM):\n"
                "    bolt dmg ~ 2 * 5.    ← 2d5, max 10\n\n"
                "Multi-dice addend (N + N + N = each die):\n"
                "    bolt dmg ~ 3 + 3 + 3.    ← 3d3, max 9\n\n"
                "Barrage loop (repeat K times, indented):\n"
                "    repeat 4:\n"
                "        bolt dmg ~ 4.\n"
                "    end.\n\n"
                "Debuff attack (scroll debuff ~ \"name\" + N):\n"
                "    bolt dmg ~ 6.\n"
                "    scroll debuff ~ \"vulnerable\" + 2.\n\n"
                "Conditional (test enemy ~~ debuff):\n"
                "    test enemy ~~ vulnerable:\n"
                "        bolt dmg ~ 2 * 5.\n"
                "    fail:\n"
                "        bolt dmg ~ 5.\n"
                "    close."
            ),
            'attack_power': (
                "bolt dmg ~ <number>.\n"
                "bolt pow ~ <number>.\n"
                "  Example:\n"
                "    bolt dmg ~ 6.\n"
                "    bolt pow ~ 2."
            ),
            'defense': (
                "bolt def ~ <number>.\n"
                "  Examples:\n"
                "    bolt def ~ 6.       ← roll 1d6 block\n"
                "    bolt def ~ 2 * 4.   ← roll 2d4 block"
            ),
            'skill': (
                "bolt heal ~ <number>.\n"
                "  Examples:\n"
                "    bolt heal ~ 8.      ← roll 1d8 healing\n"
                "    bolt heal ~ 2 * 5.  ← roll 2d5 healing"
            ),
            'power': (
                "bolt pow ~ <number>.\n"
                "  Examples:\n"
                "    bolt pow ~ 2.       ← gain 2 strength\n"
                "    bolt pow ~ 4.       ← gain 4 strength"
            ),
        }
        expected = fmt.get(card.card_type, "bolt dmg/def/heal/pow ~ <number>.")
        for line in expected.splitlines():
            self._log_message(f"  {line}", "battle")
        self._log_message("⚔️  ACTION FAILED — fix your HEROSCRIPT code and try again.", "battle")



    def _build_shop_screen(self):
        """Build the shop screen. Stores canvas refs so _show_shop can reset scrollregion."""
        frame = self._create_frame('shop')

        header = tk.Frame(frame, bg=self.COLORS['header_bg'])
        header.pack(fill=tk.X)

        tk.Label(
            header, text="🛒 BINARY BAZAAR 🛒",
            font=("Times New Roman", 28, "bold"),
            fg=self.COLORS['gold'], bg=self.COLORS['header_bg']
        ).pack(pady=15)

        self.shop_tokens = tk.Label(
            header, text="Tokens: 0",
            font=("Courier New", 14),
            fg=self.COLORS['text_primary'], bg=self.COLORS['header_bg']
        )
        self.shop_tokens.pack(pady=(0, 10))

        content = tk.Frame(frame, bg=self.COLORS['background'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # ── Cards column ──────────────────────────────────────────────────
        cards_outer = tk.LabelFrame(
            content, text="Cards for Sale  (5 items, rarity-weighted)",
            font=("Times New Roman", 12), fg=self.COLORS['blue'],
            bg=self.COLORS['background'])
        cards_outer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self._shop_cards_canvas = tk.Canvas(
            cards_outer, bg=self.COLORS['background'], highlightthickness=0)
        cards_sb = tk.Scrollbar(
            cards_outer, orient=tk.VERTICAL, command=self._shop_cards_canvas.yview)
        self.shop_cards_frame = tk.Frame(
            self._shop_cards_canvas, bg=self.COLORS['background'])
        self.shop_cards_frame.bind(
            "<Configure>",
            lambda e: self._shop_cards_canvas.configure(
                scrollregion=self._shop_cards_canvas.bbox("all")))
        self._shop_cards_canvas.create_window(
            (0, 0), window=self.shop_cards_frame, anchor="nw")
        self._shop_cards_canvas.configure(yscrollcommand=cards_sb.set)
        self._shop_cards_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cards_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._shop_cards_canvas.bind(
            "<MouseWheel>",
            lambda e: self._shop_cards_canvas.yview_scroll(
                int(-1*(e.delta/120)), "units"))

        # ── Relics column ─────────────────────────────────────────────────
        relics_outer = tk.LabelFrame(
            content, text="Relics for Sale  (5 items, rarity-weighted)",
            font=("Times New Roman", 12), fg=self.COLORS['gold'],
            bg=self.COLORS['background'])
        relics_outer.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        self._shop_relics_canvas = tk.Canvas(
            relics_outer, bg=self.COLORS['background'], highlightthickness=0)
        relics_sb = tk.Scrollbar(
            relics_outer, orient=tk.VERTICAL, command=self._shop_relics_canvas.yview)
        self.shop_relics_frame = tk.Frame(
            self._shop_relics_canvas, bg=self.COLORS['background'])
        self.shop_relics_frame.bind(
            "<Configure>",
            lambda e: self._shop_relics_canvas.configure(
                scrollregion=self._shop_relics_canvas.bbox("all")))
        self._shop_relics_canvas.create_window(
            (0, 0), window=self.shop_relics_frame, anchor="nw")
        self._shop_relics_canvas.configure(yscrollcommand=relics_sb.set)
        self._shop_relics_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        relics_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._shop_relics_canvas.bind(
            "<MouseWheel>",
            lambda e: self._shop_relics_canvas.yview_scroll(
                int(-1*(e.delta/120)), "units"))

        tk.Button(
            frame, text="Leave Shop",
            font=("Times New Roman", 14, "bold"),
            bg='#603020', fg=self.COLORS['text_primary'],
            command=self._show_map
        ).pack(pady=10)

    def _shop_card_price(self, card: Card) -> int:
        """Price = 30 base + 15 per energy + rarity surcharge."""
        rarity_bonus = {'common': 0, 'uncommon': 20, 'rare': 50, 'legendary': 100}
        return 30 + card.energy_cost * 15 + rarity_bonus.get(card.rarity, 0)

    def _shop_relic_price(self, relic: Relic) -> int:
        """Relic price scales with rarity: common cheapest, legendary most expensive."""
        return {'common': 40, 'uncommon': 80, 'rare': 140, 'legendary': 220}.get(
            relic.rarity, 60)

    def _pick_weighted(self, items: list, weights: dict,
                       key_fn, count: int) -> list:
        """
        Select exactly `count` unique items from `items` using rarity weights.
        Uniqueness is determined by key_fn(item).  Returns a list of <= count items.
        """
        # Group items by rarity, shuffle each group
        by_rarity = {'common': [], 'uncommon': [], 'rare': [], 'legendary': []}
        for item in items:
            rarity = getattr(item, 'rarity', 'common')
            by_rarity.setdefault(rarity, []).append(item)
        for lst in by_rarity.values():
            random.shuffle(lst)

        # Build a weighted flat list of (item, weight) where each item appears once
        # We use the weight as the probability mass, then do weighted sampling
        unique_items = []
        seen_keys = set()
        for rarity, lst in by_rarity.items():
            w = weights.get(rarity, 1)
            for item in lst:
                k = key_fn(item)
                if k not in seen_keys:
                    seen_keys.add(k)
                    unique_items.append((item, w))

        if not unique_items:
            return []

        # Weighted sample without replacement
        selected = []
        pool = list(unique_items)
        for _ in range(min(count, len(pool))):
            total = sum(w for _, w in pool)
            if total == 0:
                break
            r = random.uniform(0, total)
            cumulative = 0
            chosen_idx = 0
            for idx, (item, w) in enumerate(pool):
                cumulative += w
                if r <= cumulative:
                    chosen_idx = idx
                    break
            selected.append(pool[chosen_idx][0])
            pool.pop(chosen_idx)

        return selected

    def _show_shop(self):
        """
        Pick exactly 5 rarity-weighted cards and 5 rarity-weighted relics.
        Tears down and rebuilds the inner scroll frames from scratch every call
        so zero stale widgets can survive between visits.
        """
        if not self.game:
            return

        self._show_frame('shop')
        self.shop_tokens.config(text=f"Tokens: {self.game.player.tokens}")

        floor = self.game.floor

        # Floor-gated card pool
        pool = list(CardLibrary.STARTER_CARDS) + list(CardLibrary.TIER1_CARDS)
        if floor >= 2:
            pool.extend(CardLibrary.TIER2_CARDS)
        if floor >= 5:
            pool.extend(CardLibrary.TIER3_CARDS)
            pool.extend(CardLibrary.SPECIAL_CARDS)

        # Rarity weights shift toward rarer at higher floors
        if floor <= 3:
            weights = {'common': 55, 'uncommon': 30, 'rare': 12, 'legendary': 3}
        elif floor <= 7:
            weights = {'common': 35, 'uncommon': 35, 'rare': 22, 'legendary': 8}
        else:
            weights = {'common': 20, 'uncommon': 30, 'rare': 30, 'legendary': 20}

        # Select exactly 5 unique cards and 5 unique relics
        self.shop_cards = self._pick_weighted(
            pool, weights, key_fn=lambda c: c.name, count=5)
        self.shop_cards.sort(key=lambda c: (c.energy_cost, c.name))

        self.shop_relics = self._pick_weighted(
            RelicLibrary.RELICS, weights, key_fn=lambda r: r.name, count=5)

        # ── Rebuild the cards inner frame from scratch ────────────────────
        # Destroy the old frame entirely (removes all children with it)
        if hasattr(self, 'shop_cards_frame') and self.shop_cards_frame.winfo_exists():
            self.shop_cards_frame.destroy()
        self.shop_cards_frame = tk.Frame(
            self._shop_cards_canvas, bg=self.COLORS['background'])
        self.shop_cards_frame.bind(
            "<Configure>",
            lambda e: self._shop_cards_canvas.configure(
                scrollregion=self._shop_cards_canvas.bbox("all")))
        self._shop_cards_canvas.delete("all")
        self._shop_cards_canvas.create_window(
            (0, 0), window=self.shop_cards_frame, anchor="nw")
        self._shop_cards_canvas.yview_moveto(0)

        # ── Rebuild the relics inner frame from scratch ───────────────────
        if hasattr(self, 'shop_relics_frame') and self.shop_relics_frame.winfo_exists():
            self.shop_relics_frame.destroy()
        self.shop_relics_frame = tk.Frame(
            self._shop_relics_canvas, bg=self.COLORS['background'])
        self.shop_relics_frame.bind(
            "<Configure>",
            lambda e: self._shop_relics_canvas.configure(
                scrollregion=self._shop_relics_canvas.bbox("all")))
        self._shop_relics_canvas.delete("all")
        self._shop_relics_canvas.create_window(
            (0, 0), window=self.shop_relics_frame, anchor="nw")
        self._shop_relics_canvas.yview_moveto(0)

        # Let Tk process the destructions before populating
        self.root.update_idletasks()

        # Render exactly 5 cards
        for card in self.shop_cards:
            self._create_shop_card(card, self.shop_cards_frame)

        # Render exactly 5 relics
        for relic in self.shop_relics:
            self._create_shop_relic(relic, self.shop_relics_frame)

    def _create_shop_card(self, card: Card, parent: tk.Frame):
        """One card listing: rarity-coloured frame, full HEROSCRIPT code, buy button."""
        price      = self._shop_card_price(card)
        can_afford = bool(self.game) and self.game.player.tokens >= price

        bg_map = {
            'common': '#3a3a3a', 'uncommon': '#1e4a1e',
            'rare':   '#1a3060', 'legendary': '#5a2800',
        }
        bg = bg_map.get(card.rarity, '#333333')

        item = tk.Frame(parent, bg=bg, bd=2, relief=tk.RIDGE)
        item.pack(fill=tk.X, pady=3, padx=4)

        hdr = tk.Frame(item, bg=bg)
        hdr.pack(fill=tk.X, padx=6, pady=(4, 0))
        tk.Label(hdr, text=card.name,
                 font=("Courier New", 10, "bold"),
                 fg='#ffffff', bg=bg).pack(side=tk.LEFT)
        tk.Label(hdr, text=f"  {card.energy_cost}E  [{card.rarity}]",
                 font=("Courier New", 8), fg='#cccccc', bg=bg).pack(side=tk.LEFT)

        tk.Label(item, text=card.description,
                 font=("Courier New", 8, "italic"),
                 fg='#aaccff', bg=bg, anchor="w").pack(fill=tk.X, padx=6)

        # Full HEROSCRIPT code in a small readonly text widget
        code_lines = card.code.strip().split('\n')
        code_box = tk.Text(item, height=min(len(code_lines), 5),
                           font=("Courier New", 8),
                           bg='#050818', fg='#88ff88',
                           relief=tk.FLAT, state=tk.DISABLED, wrap=tk.NONE)
        code_box.config(state=tk.NORMAL)
        code_box.insert(tk.END, card.code.strip())
        code_box.config(state=tk.DISABLED)
        code_box.pack(fill=tk.X, padx=6, pady=2)

        btn_row = tk.Frame(item, bg=bg)
        btn_row.pack(fill=tk.X, padx=6, pady=(0, 4))
        tk.Label(btn_row, text=f"[{card.card_type.upper()}]",
                 font=("Courier New", 8), fg='#ffcc44', bg=bg).pack(side=tk.LEFT)
        tk.Button(btn_row,
                  text=f"Buy — {price} tokens",
                  font=("Courier New", 9, "bold"),
                  bg='#228B22' if can_afford else '#404040',
                  fg='#ffffff',
                  cursor="hand2" if can_afford else "arrow",
                  command=lambda c=card, p=price: self._buy_card(c, p)
                  ).pack(side=tk.RIGHT)

    def _create_shop_relic(self, relic: Relic, parent: tk.Frame):
        """One relic listing: rarity-coloured frame, description, buy button."""
        price      = self._shop_relic_price(relic)
        can_afford = bool(self.game) and self.game.player.tokens >= price

        bg_map = {
            'common': '#383838', 'uncommon': '#1e3e1e',
            'rare':   '#182848', 'legendary': '#4e2000',
        }
        rar_fg = {
            'common': '#bbbbbb', 'uncommon': '#88ee88',
            'rare':   '#6699ff', 'legendary': '#ffaa00',
        }
        bg  = bg_map.get(relic.rarity, '#333333')
        fgr = rar_fg.get(relic.rarity, '#cccccc')

        item = tk.Frame(parent, bg=bg, bd=2, relief=tk.RIDGE)
        item.pack(fill=tk.X, pady=3, padx=4)

        hdr = tk.Frame(item, bg=bg)
        hdr.pack(fill=tk.X, padx=6, pady=(4, 0))
        tk.Label(hdr, text=relic.name,
                 font=("Courier New", 10, "bold"),
                 fg='#ffffff', bg=bg).pack(side=tk.LEFT)
        tk.Label(hdr, text=f"  [{relic.rarity}]",
                 font=("Courier New", 8), fg=fgr, bg=bg).pack(side=tk.LEFT)

        tk.Label(item, text=relic.description,
                 font=("Courier New", 9), fg='#dddddd', bg=bg, anchor="w"
                 ).pack(fill=tk.X, padx=6, pady=(0, 2))

        btn_row = tk.Frame(item, bg=bg)
        btn_row.pack(fill=tk.X, padx=6, pady=(0, 4))
        tk.Button(btn_row,
                  text=f"Buy — {price} tokens",
                  font=("Courier New", 9, "bold"),
                  bg='#228B22' if can_afford else '#404040',
                  fg='#ffffff',
                  cursor="hand2" if can_afford else "arrow",
                  command=lambda r=relic, p=price: self._buy_relic(r, p)
                  ).pack(side=tk.RIGHT)

    def _buy_card(self, card: Card, price: int = None):
        """Deduct tokens, add card to player collection, refresh shop."""
        if not self.game:
            return
        if price is None:
            price = self._shop_card_price(card)
        if self.game.player.tokens < price:
            return
        self.game.player.tokens -= price
        self.game.player.add_card_to_deck(card)
        self._show_shop()

    def _buy_relic(self, relic: Relic, price: int = None):
        """Deduct tokens, add relic to player inventory, refresh shop."""
        if not self.game:
            return
        if price is None:
            price = self._shop_relic_price(relic)
        if self.game.player.tokens < price:
            return
        if len(self.game.player.relics) >= self.game.player.max_relics:
            return
        self.game.player.tokens -= price
        self.game.player.add_relic(relic)
        self._show_shop()

    def _remove_card(self, card_index: int):
        """Remove a card from the equipped deck."""
        if self.game and 0 <= card_index < len(self.game.player.equipped_cards):
            self.game.remove_card(card_index)
            self._show_inventory()

    def _remove_relic(self, relic_index: int):
        """Permanently remove a relic from inventory."""
        if self.game and 0 <= relic_index < len(self.game.player.relics):
            relic = self.game.player.relics[relic_index]
            self.game.player.remove_relic(relic)
            self._show_inventory()

    def _equip_card(self, card: Card):
        """Equip a card to the active deck."""
        if self.game and len(self.game.player.equipped_cards) < 10:
            if card not in self.game.player.equipped_cards:
                self.game.player.equipped_cards.append(card)
                self.game.player.deck.append(card)
                self._show_inventory()

    def _unequip_card(self, card: Card):
        """Unequip a card from the active deck."""
        if self.game and card in self.game.player.equipped_cards:
            self.game.player.equipped_cards.remove(card)
            if card in self.game.player.deck:
                self.game.player.deck.remove(card)
            if card in self.game.player.hand:
                self.game.player.hand.remove(card)
            self._show_inventory()

    def _unequip_relic(self, relic_index: int):
        """Unequip a relic from equipped relics and keep in inventory."""
        if self.game and 0 <= relic_index < len(self.game.player.equipped_relics):
            relic = self.game.player.equipped_relics[relic_index]
            self.game.player.unequip_relic(relic)
            self._show_inventory()



    def _build_reward_screen(self):
        """Build the reward screen."""
        frame = self._create_frame('reward')


        header = tk.Frame(frame, bg=self.COLORS['header_bg'])
        header.pack(fill=tk.X, pady=20)

        tk.Label(
            header,
            text="⚔️ VICTORY! ⚔️",
            font=("Times New Roman", 32, "bold"),
            fg=self.COLORS['gold'],
            bg=self.COLORS['header_bg']
        ).pack(pady=10)

        tk.Label(
            header,
            text="Choose a card reward:",
            font=("Times New Roman", 14),
            fg=self.COLORS['text_primary'],
            bg=self.COLORS['header_bg']
        ).pack(pady=(0, 10))


        self.reward_cards_container = tk.Frame(frame, bg=self.COLORS['background'])
        self.reward_cards_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)


        bottom = tk.Frame(frame, bg=self.COLORS['background'])
        bottom.pack(fill=tk.X, pady=10)

        tk.Button(
            bottom,
            text="Skip Reward",
            font=("Times New Roman", 12),
            bg='#503030',
            fg=self.COLORS['text_primary'],
            command=self._skip_reward
        ).pack(side=tk.LEFT, padx=20)

    def _show_reward_screen(self):
        """Show the reward/card selection screen."""
        self._show_frame('reward')


        for widget in self.reward_cards_container.winfo_children():
            widget.destroy()


        if not self.game or not self.game.player:
            return

        floor = self.game.floor


        all_available_cards = CardLibrary.TIER1_CARDS + CardLibrary.TIER2_CARDS + CardLibrary.TIER3_CARDS
        reward_cards = random.sample(all_available_cards, min(3, len(all_available_cards)))


        for card in reward_cards:
            self._create_reward_card(card)

    def _create_reward_card(self, card: Card):
        """Create a reward card button."""
        card_frame = tk.Frame(self.reward_cards_container, bg=self.COLORS['panel_bg'], bd=3, relief=tk.RAISED)
        card_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10, padx=10)


        header = tk.Frame(card_frame, bg=card.get_color() if hasattr(card, 'get_color') else self.COLORS['gold'])
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text=f"{card.name}",
            font=("Times New Roman", 16, "bold"),
            fg=self.COLORS['text_primary'],
            bg=card.get_color() if hasattr(card, 'get_color') else self.COLORS['gold']
        ).pack(pady=10)


        body = tk.Frame(card_frame, bg=self.COLORS['panel_bg'])
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(
            body,
            text=f"Energy Cost: {card.energy_cost}",
            font=("Courier New", 10, "bold"),
            fg=self.COLORS['blue'],
            bg=self.COLORS['panel_bg']
        ).pack()

        tk.Label(
            body,
            text=f"Type: {card.card_type}",
            font=("Courier New", 10),
            fg=self.COLORS['text_secondary'],
            bg=self.COLORS['panel_bg']
        ).pack()

        tk.Label(
            body,
            text=f"Rarity: {card.rarity}",
            font=("Courier New", 10),
            fg=self.COLORS['purple'],
            bg=self.COLORS['panel_bg']
        ).pack()

        tk.Label(
            body,
            text=f"Code:\n{card.code}",
            font=("Courier New", 9, "bold"),
            fg=self.COLORS['text_primary'],
            bg=self.COLORS['panel_bg'],
            wraplength=400
        ).pack(pady=5)

        tk.Label(
            body,
            text=f"Code: {card.code}",
            font=("Courier New", 8),
            fg=self.COLORS['text_secondary'],
            bg=self.COLORS['panel_bg']
        ).pack()


        tk.Button(
            body,
            text="⭐ SELECT THIS CARD ⭐",
            font=("Times New Roman", 12, "bold"),
            bg=self.COLORS['green'],
            fg=self.COLORS['background'],
            command=lambda c=card: self._select_reward_card(c)
        ).pack(pady=10, fill=tk.X)

    def _select_reward_card(self, card: Card):
        """Select a reward card and return to map."""
        if self.game:
            self.game.player.add_card_to_deck(card)
        self._show_map()

    def _skip_reward(self):
        """Skip the reward and return to map."""
        self._show_map()



    def _build_inventory_screen(self):
        """Build the inventory screen."""
        frame = self._create_frame('inventory')


        header = tk.Frame(frame, bg=self.COLORS['header_bg'])
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="📦 INVENTORY 📦",
            font=("Times New Roman", 28, "bold"),
            fg=self.COLORS['gold'],
            bg=self.COLORS['header_bg']
        ).pack(pady=15)


        content = tk.Frame(frame, bg=self.COLORS['background'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)


        relics_frame = tk.LabelFrame(
            content,
            text="Relics (Max 3 Equipped)",
            font=("Times New Roman", 14),
            fg=self.COLORS['gold'],
            bg=self.COLORS['background']
        )
        relics_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)


        relics_canvas = tk.Canvas(relics_frame, bg=self.COLORS['background'], highlightthickness=0, height=200)
        relics_scrollbar = tk.Scrollbar(relics_frame, orient="vertical", command=relics_canvas.yview)
        self.relics_scrollable_frame = tk.Frame(relics_canvas, bg=self.COLORS['background'])

        self.relics_scrollable_frame.bind(
            "<Configure>",
            lambda e: relics_canvas.configure(scrollregion=relics_canvas.bbox("all"))
        )

        relics_canvas.create_window((0, 0), window=self.relics_scrollable_frame, anchor="nw")
        relics_canvas.configure(yscrollcommand=relics_scrollbar.set)

        relics_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        relics_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


        cards_frame = tk.LabelFrame(
            content,
            text="Deck",
            font=("Times New Roman", 14),
            fg=self.COLORS['blue'],
            bg=self.COLORS['background']
        )
        cards_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)


        cards_canvas = tk.Canvas(cards_frame, bg=self.COLORS['background'], highlightthickness=0, height=200)
        cards_scrollbar = tk.Scrollbar(cards_frame, orient="vertical", command=cards_canvas.yview)
        self.cards_scrollable_frame = tk.Frame(cards_canvas, bg=self.COLORS['background'])

        self.cards_scrollable_frame.bind(
            "<Configure>",
            lambda e: cards_canvas.configure(scrollregion=cards_canvas.bbox("all"))
        )

        cards_canvas.create_window((0, 0), window=self.cards_scrollable_frame, anchor="nw")
        cards_canvas.configure(yscrollcommand=cards_scrollbar.set)

        cards_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        cards_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


        tk.Button(
            frame,
            text="← Back to Map",
            font=("Times New Roman", 12),
            bg='#4a3060',
            fg=self.COLORS['text_primary'],
            command=self._show_map
        ).pack(pady=15)

    def _show_inventory(self):
        """Update and show the inventory screen."""
        if not self.game:
            return

        self._show_frame('inventory')


        for widget in self.relics_scrollable_frame.winfo_children():
            widget.destroy()


        if not self.game.player.relics and not self.game.player.equipped_relics:
            tk.Label(
                self.relics_scrollable_frame,
                text="No relics collected",
                font=("Courier New", 10),
                fg=self.COLORS['text_secondary'],
                bg=self.COLORS['background']
            ).pack(pady=20)
        else:

            if self.game.player.equipped_relics:
                tk.Label(
                    self.relics_scrollable_frame,
                    text="Equipped:",
                    font=("Courier New", 10, "bold"),
                    fg=self.COLORS['blue'],
                    bg=self.COLORS['background']
                ).pack(anchor=tk.W, pady=(0,4), padx=5)
                for i, relic in enumerate(self.game.player.equipped_relics):
                    relic_frame = tk.Frame(self.relics_scrollable_frame, bg=self.COLORS['panel_bg'])
                    relic_frame.pack(fill=tk.X, pady=2, padx=5)

                    tk.Label(
                        relic_frame,
                        text=f"★ {relic.name}: {relic.description}",
                        font=("Courier New", 9),
                        fg=self.COLORS['gold'],
                        bg=self.COLORS['panel_bg']
                    ).pack(anchor=tk.W, side=tk.LEFT, padx=5, pady=2, fill=tk.X, expand=True)

                    tk.Button(
                        relic_frame,
                        text="Unequip",
                        font=("Courier New", 8),
                        bg='#503020',
                        fg=self.COLORS['red'],
                        command=lambda idx=i: self._unequip_relic(idx)
                    ).pack(side=tk.RIGHT, padx=5)


            if self.game.player.relics:
                tk.Label(
                    self.relics_scrollable_frame,
                    text="Inventory:",
                    font=("Courier New", 10, "bold"),
                    fg=self.COLORS['blue'],
                    bg=self.COLORS['background']
                ).pack(anchor=tk.W, pady=(10,4), padx=5)
                for i, relic in enumerate(self.game.player.relics):
                    relic_frame = tk.Frame(self.relics_scrollable_frame, bg=self.COLORS['panel_bg'])
                    relic_frame.pack(fill=tk.X, pady=2, padx=5)

                    tk.Label(
                        relic_frame,
                        text=f"• {relic.name}: {relic.description}",
                        font=("Courier New", 9),
                        fg=self.COLORS['gold'],
                        bg=self.COLORS['panel_bg']
                    ).pack(anchor=tk.W, side=tk.LEFT, padx=5, pady=2, fill=tk.X, expand=True)

                    can_equip = len(self.game.player.equipped_relics) < self.game.player.max_equipped_relics
                    tk.Button(
                        relic_frame,
                        text="Equip",
                        font=("Courier New", 8),
                        bg='#204020' if can_equip else '#404040',
                        fg=self.COLORS['text_primary'],
                        state=tk.NORMAL if can_equip else tk.DISABLED,
                        command=lambda idx=i: (self.game.player.equip_relic(self.game.player.relics[idx]), self._show_inventory())
                    ).pack(side=tk.RIGHT, padx=5)


        for widget in self.cards_scrollable_frame.winfo_children():
            widget.destroy()


        if not self.game.player.all_cards:
            tk.Label(
                self.cards_scrollable_frame,
                text="No cards collected",
                font=("Courier New", 10),
                fg=self.COLORS['text_secondary'],
                bg=self.COLORS['background']
            ).pack(pady=20)
        else:
            for i, card in enumerate(self.game.player.all_cards):
                is_equipped = card in self.game.player.equipped_cards
                card_frame = tk.Frame(self.cards_scrollable_frame, bg=self.COLORS['panel_bg'])
                card_frame.pack(fill=tk.X, pady=2, padx=5)


                status = "✓" if is_equipped else "○"
                status_color = self.COLORS['green'] if is_equipped else self.COLORS['text_secondary']

                tk.Label(
                    card_frame,
                    text=f"{status} {card.energy_cost}E {card.name}: {card.code[:20]}",
                    font=("Courier New", 9),
                    fg=status_color if is_equipped else self.COLORS['text_primary'],
                    bg=self.COLORS['panel_bg']
                ).pack(anchor=tk.W, side=tk.LEFT, padx=5, pady=2, fill=tk.X, expand=True)


                if is_equipped:
                    tk.Button(
                        card_frame,
                        text="Unequip",
                        font=("Courier New", 8),
                        bg='#503020',
                        fg=self.COLORS['red'],
                        command=lambda card_obj=card: self._unequip_card(card_obj)
                    ).pack(side=tk.RIGHT, padx=5)
                else:
                    can_equip = len(self.game.player.equipped_cards) < 10
                    tk.Button(
                        card_frame,
                        text="Equip",
                        font=("Courier New", 8),
                        bg='#205030' if can_equip else '#404040',
                        fg=self.COLORS['green'] if can_equip else self.COLORS['text_secondary'],
                        command=lambda card_obj=card: self._equip_card(card_obj),
                        state=tk.NORMAL if can_equip else tk.DISABLED
                    ).pack(side=tk.RIGHT, padx=5)



    def _build_end_screen(self):
        """Build the victory/defeat screen."""
        frame = self._create_frame('end')

        self.end_title = tk.Label(
            frame,
            text="",
            font=("Times New Roman", 48, "bold"),
            fg=self.COLORS['gold'],
            bg=self.COLORS['background']
        )
        self.end_title.pack(pady=40)

        self.end_message = tk.Label(
            frame,
            text="",
            font=("Times New Roman", 16),
            fg=self.COLORS['text_primary'],
            bg=self.COLORS['background']
        )
        self.end_message.pack(pady=20)

        tk.Button(
            frame,
            text="Return to Main Menu",
            font=("Times New Roman", 16, "bold"),
            bg='#305050',
            fg=self.COLORS['text_primary'],
            command=lambda: self._show_frame('main_menu')
        ).pack(pady=30)

    def _show_end_screen(self, victory: bool):
        """Show the end screen."""
        self._show_frame('end')

        if victory:
            self.end_title.config(text="🏆 VICTORY! 🏆", fg=self.COLORS['gold'])
            self.end_message.config(
                text="You have conquered The Heart of the Spire!\n"
                     "All 15 floors cleared!",
                fg=self.COLORS['green']
            )
        else:
            self.end_title.config(text="💀 DEFEAT 💀", fg=self.COLORS['red'])
            self.end_message.config(
                text="You have fallen in battle...\n"
                     "The dungeon claims another soul.",
                fg=self.COLORS['red']
            )



    def _build_help_screen(self):
        """Build the help screen."""
        frame = self._create_frame('help')


        header = tk.Frame(frame, bg=self.COLORS['header_bg'])
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="📜 THE HEROSCRIPT GUIDE 📜",
            font=("Times New Roman", 28, "bold"),
            fg=self.COLORS['gold'],
            bg=self.COLORS['header_bg']
        ).pack(pady=15)

        tk.Button(
            header,
            text="← Back to Menu",
            font=("Times New Roman", 12),
            bg='#4a3020',
            fg=self.COLORS['gold'],
            command=lambda: self._show_frame('main_menu')
        ).pack(pady=10)


        help_frame = tk.Frame(frame, bg=self.COLORS['background'])
        help_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        help_text = """
═══════════════════════════════════════════════════════════════
HOW TO PLAY
═══════════════════════════════════════════════════════════════

1. CHOOSE YOUR CLASS - Select one of 7 unique heroes
2. NAVIGATE THE MAP - Click on glowing nodes to progress
3. BATTLE ENEMIES - Click cards, then press "Play Card"
4. MANAGE ENERGY - Each card costs energy to play
5. BUILD YOUR DECK - Buy cards at shops, collect relics
6. DEFEAT THE BOSS - Clear all 15 floors to win!

═══════════════════════════════════════════════════════════════
COMBAT SYSTEM
═══════════════════════════════════════════════════════════════

• Each turn you draw 5 cards and get energy
• Click a card to select it, then press "Play Card"
• Cards deal damage, gain block, or provide other effects
• Block absorbs damage but resets each turn
• Strength adds bonus damage to your attacks
• End your turn when ready - enemy attacks!

═══════════════════════════════════════════════════════════════
CARD HEROSCRIPT (HeroScript Language)
═══════════════════════════════════════════════════════════════

Cards use the HeroScript programming language:

• 'bolt dmg ~ 6.' = Roll 1d6 damage
• 'bolt def ~ 8.' = Roll 1d8 block
• 'bolt heal ~ 4.' = Roll 1d4 healing
• 'bolt pow ~ 2.' = Gain 2 strength
• '4 + 4' = Roll 2d4 (total max 8)
• 'bolt dmg ~ 2 + 2.' = Roll 2d2 damage

MANA COSTS:
• 1 mana: max 5 damage
• 2 mana: max 6-10 damage
• 3 mana: max 11-16 damage
• 4 mana: max 17+ damage

═══════════════════════════════════════════════════════════════
MAP NODES
═══════════════════════════════════════════════════════════════

⚔️ ENEMY - Battle for tokens and cards
💀 ELITE - Harder battles, better rewards
🏪 SHOP - Buy cards and relics
🏕️ REST - Heal 30% of max HP
💎 TREASURE - Get tokens and cards
❓ EVENT - Random good/bad effects
👹 BOSS - Final enemy on floor 15

═══════════════════════════════════════════════════════════════
CLASSES
═══════════════════════════════════════════════════════════════

IRONCLAD - High HP (90), heals 1 HP per turn
SILENT - Block after attacking, fast cards
DEFECT - +1 energy if no attack last turn
WATCHER - +1 strength on odd turns
GLASS CANNON - Low HP (40), 25% crit chance
NECROMANCER - Heal 2 HP when enemy dies
CHRONOMANCER - 20% chance for extra turn

═══════════════════════════════════════════════════════════════
RELICS (Max 3 equipped)
═══════════════════════════════════════════════════════════════

• Red Idol: +1 damage
• Golden Shield: +1 block
• Silver Boots: +1 energy
• Sword Charm: +2 damage
• Arcane Eye: Draw +1 card
• War Horn: +3 first attack damage
• Phoenix Feather: Heal 5 at combat start
        """

        text_widget = scrolledtext.ScrolledText(
            help_frame,
            wrap=tk.WORD,
            font=("Courier New", 10),
            fg=self.COLORS['text_primary'],
            bg=self.COLORS['background'],
            relief=tk.FLAT,
            bd=0
        )
        text_widget.insert(tk.END, help_text)
        text_widget.configure(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)

    def _show_help(self):
        """Show the help screen."""
        self._show_frame('help')



# Entry point: create Tk root, instantiate GUI, start event loop.
def main():
    root = tk.Tk()
    app = CodeSpireGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()